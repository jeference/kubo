"""Cotas (RN-02 a RN-05) e teto global de gasto (RN-06, RN-07)."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone

from accounts.models import Visitor
from common.alerts import alert
from common.exceptions import QuotaExceeded, ServiceBusy
from creations.fsm import TASK_ACTIVE
from creations.models import ProviderTask, QuotaReservation

_COUNTED = (QuotaReservation.State.RESERVED, QuotaReservation.State.CONSUMED)
_TASK_KIND_TO_QUOTA = {
    ProviderTask.Kind.TEXT_TO_IMAGE: QuotaReservation.Kind.IMAGE,
    ProviderTask.Kind.PHOTO_TO_IMAGE: QuotaReservation.Kind.IMAGE,
    ProviderTask.Kind.IMAGE_EDIT: QuotaReservation.Kind.EDIT,
}
_LIMIT_MESSAGES = {
    QuotaReservation.Kind.IMAGE: "Você atingiu o limite de imagens de hoje.",
    QuotaReservation.Kind.EDIT: "Você atingiu o limite de edições de hoje.",
}


def _used(*, field: str, value: str, kind: str, day) -> int:
    return QuotaReservation.objects.filter(
        **{field: value}, kind=kind, day=day, state__in=_COUNTED
    ).count()


def _lock_actor(actor) -> None:
    """Serializa as reservas de um mesmo ator, evitando passar do limite em pedidos simultâneos."""
    if actor.user is not None:
        actor.user.__class__.objects.select_for_update().get(pk=actor.user.pk)
    else:
        Visitor.objects.select_for_update().get(pk=actor.visitor.pk)


def daily_spend_usd() -> Decimal:
    """Custo informado pelo provedor no dia, mais a estimativa do que ainda está em andamento."""
    today = timezone.localdate()
    start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    tasks = ProviderTask.objects.filter(created_at__gte=start)
    spent = tasks.aggregate(total=Sum("cost_usd"))["total"] or Decimal(0)
    estimates = settings.BUSINESS["ESTIMATED_COST_USD"]
    for kind, quota_kind in _TASK_KIND_TO_QUOTA.items():
        active = tasks.filter(kind=kind, status__in=TASK_ACTIVE).count()
        spent += Decimal(str(estimates[quota_kind])) * active
    return spent


def ensure_spend_cap() -> None:
    cap = Decimal(str(settings.BUSINESS["DAILY_SPEND_CAP_USD"]))
    if daily_spend_usd() < cap:
        return
    # Um alerta por dia: `cache.add` só grava se a chave não existir.
    if cache.add(f"spend_cap_alert:{timezone.localdate()}", 1, timeout=24 * 3600):
        alert("daily_spend_cap_reached", cap_usd=str(cap))
    raise ServiceBusy(
        "Estamos com muita procura agora. Tente de novo em algumas horas.",
        code="generation_paused",
    )


def reserve(*, actor, ip_hash: str, task_kind: str) -> str:
    """Valida limites do ator e do IP. Devolve o tipo de cota. Chame dentro de uma transação."""
    _lock_actor(actor)
    ensure_spend_cap()
    kind = _TASK_KIND_TO_QUOTA[task_kind]
    day = timezone.localdate()
    business = settings.BUSINESS

    if (
        _used(field="actor_key", value=actor.key, kind=kind, day=day)
        >= (business["QUOTA_PER_DAY"][kind])
    ):
        raise QuotaExceeded(_LIMIT_MESSAGES[kind], extra={"quota_kind": kind})
    if (
        ip_hash
        and _used(field="ip_hash", value=ip_hash, kind=kind, day=day)
        >= (business["QUOTA_PER_IP_PER_DAY"][kind])
    ):
        raise QuotaExceeded(_LIMIT_MESSAGES[kind], extra={"quota_kind": kind})

    active = ProviderTask.objects.filter(actor.creation_tasks_filter(), status__in=TASK_ACTIVE)
    if active.count() >= business["MAX_ACTIVE_TASKS"]:
        raise QuotaExceeded(
            "Aguarde as gerações em andamento terminarem.", code="too_many_active_tasks"
        )
    return kind


def attach(*, actor, ip_hash: str, kind: str, task: ProviderTask) -> QuotaReservation:
    return QuotaReservation.objects.create(
        actor_key=actor.key, ip_hash=ip_hash, kind=kind, day=timezone.localdate(), task=task
    )


def consume(task: ProviderTask) -> None:
    QuotaReservation.objects.filter(task=task, state=QuotaReservation.State.RESERVED).update(
        state=QuotaReservation.State.CONSUMED
    )


def release(task: ProviderTask) -> None:
    QuotaReservation.objects.filter(task=task, state=QuotaReservation.State.RESERVED).update(
        state=QuotaReservation.State.RELEASED
    )


def usage_for(actor) -> dict:
    day = timezone.localdate()
    limits = settings.BUSINESS["QUOTA_PER_DAY"]
    result = {}
    for kind, limit in limits.items():
        used = _used(field="actor_key", value=actor.key, kind=kind, day=day)
        result[kind] = {"limit": limit, "used": used, "remaining": max(limit - used, 0)}
    return result
