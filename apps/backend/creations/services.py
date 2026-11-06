"""Criações: ações do cliente. A API só cria tarefas; quem as executa é o worker."""

from __future__ import annotations

import io
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageStat

from catalog import prompts
from common.exceptions import GuardFailed, ResourceNotFound
from common.fsm import apply_transition
from creations import quota
from creations.fsm import CREATION_FSM, TASK_ACTIVE
from creations.models import Creation, CreationInput, ProviderTask
from media import services as media
from media.models import Asset

_BACKGROUND_MIN_MEDIAN = 245
_BACKGROUND_MAX_STDDEV = 5
_BACKGROUND_STRIP_RATIO = 0.02


def creations_for(actor):
    return Creation.objects.filter(actor.owner_filter(), deleted_at__isnull=True)


def get_creation(actor, creation_id) -> Creation:
    creation = (
        creations_for(actor)
        .select_related("input", "input__photo", "current_version")
        .filter(globalid=creation_id)
        .first()
    )
    if creation is None:
        raise ResourceNotFound("Criação não encontrada.")
    return creation


def get_creation_for_response(creation: Creation) -> Creation:
    """Recarrega com o que o serializer usa, depois de uma ação."""
    return (
        Creation.objects.select_related("input", "input__photo", "current_version")
        .prefetch_related("versions__asset", "versions__parent")
        .get(pk=creation.pk)
    )


def _new_task(*, actor, ip_hash: str, creation: Creation, kind: str, **fields) -> ProviderTask:
    quota_kind = quota.reserve(actor=actor, ip_hash=ip_hash, task_kind=kind)
    task = ProviderTask.objects.create(
        creation=creation,
        kind=kind,
        prompt_version=prompts.PROMPT_VERSION,
        next_attempt_at=timezone.now(),
        **fields,
    )
    quota.attach(actor=actor, ip_hash=ip_hash, kind=quota_kind, task=task)
    return task


def start_creation(
    *,
    actor,
    ip_hash: str,
    text: str,
    style: str,
    photo_bytes: bytes | None,
    rights_accepted: bool,
    request_id: str = "",
) -> Creation:
    text = text.strip()
    if style not in prompts.STYLE_IDS:
        raise GuardFailed("Estilo inválido.", code="invalid_style")
    if not text and photo_bytes is None:
        raise GuardFailed("Descreva o que você quer ou envie uma foto.", code="empty_input")
    if photo_bytes is not None and not rights_accepted:
        raise GuardFailed(
            "Confirme que você tem direitos sobre a foto e o consentimento de quem aparece nela.",
            code="rights_required",
        )
    normalized = media.normalize_photo(photo_bytes) if photo_bytes is not None else None
    photo = (
        media.store(data=normalized, kind=Asset.Kind.PHOTO, mime="image/png")
        if (normalized is not None)
        else None
    )

    with transaction.atomic():
        creation = Creation.objects.create(style=style, **actor.owner_fields())
        CreationInput.objects.create(
            creation=creation,
            text=text,
            photo=photo,
            rights_accepted_at=timezone.now() if photo is not None else None,
            rights_accepted_ip_hash=ip_hash if photo is not None else "",
            terms_version=settings.BUSINESS["TERMS_VERSION"] if photo is not None else "",
        )
        _enqueue_image(actor=actor, ip_hash=ip_hash, creation=creation)
        _record_started(creation, actor, request_id)
    return creation


def _record_started(creation: Creation, actor, request_id: str) -> None:
    from audit.services import record_event

    record_event(
        instance=creation,
        event="created",
        to_state=creation.status,
        actor=actor,
        request_id=request_id,
    )


def _enqueue_image(*, actor, ip_hash: str, creation: Creation) -> ProviderTask:
    source = creation.input
    if source.photo_id:
        kind = ProviderTask.Kind.PHOTO_TO_IMAGE
        prompt = prompts.photo_prompt(style=creation.style, request=source.text)
    else:
        kind = ProviderTask.Kind.TEXT_TO_IMAGE
        prompt = prompts.text_prompt(style=creation.style, text=source.text)
    return _new_task(
        actor=actor,
        ip_hash=ip_hash,
        creation=creation,
        kind=kind,
        rendered_prompt=prompt,
    )


def retry(*, actor, ip_hash: str, creation: Creation, request_id: str = "") -> Creation:
    """Tenta a imagem de novo. Uma nova reserva de cota: a anterior foi devolvida."""

    def effects():
        creation.last_error_code = ""
        creation.last_error_message = ""
        creation.save(update_fields=["last_error_code", "last_error_message", "updated_at"])
        _enqueue_image(actor=actor, ip_hash=ip_hash, creation=creation)

    apply_transition(
        instance=creation,
        fsm=CREATION_FSM,
        event="retry",
        actor=actor,
        effects=effects,
        request_id=request_id,
    )
    creation.refresh_from_db()
    return creation


def request_edit(
    *, actor, ip_hash: str, creation: Creation, instruction: str, version_id
) -> ProviderTask:
    instruction = instruction.strip()
    if not instruction:
        raise GuardFailed("Descreva o ajuste.", code="empty_instruction")
    if len(instruction) > settings.BUSINESS["EDIT_MAX_CHARS"]:
        raise GuardFailed("Instrução longa demais.", code="instruction_too_long")
    if creation.status != Creation.Status.READY:
        raise GuardFailed("Esta criação não pode ser editada agora.", code="not_editable")
    version = creation.versions.filter(globalid=version_id).first()
    if version is None:
        raise ResourceNotFound("Versão não encontrada.")
    with transaction.atomic():
        return _new_task(
            actor=actor,
            ip_hash=ip_hash,
            creation=creation,
            kind=ProviderTask.Kind.IMAGE_EDIT,
            source_version=version,
            instruction=instruction,
            rendered_prompt=prompts.edit_prompt(instruction=instruction),
        )


def cancel_edit(*, creation: Creation, task_id) -> ProviderTask:
    """Oculta o resultado. Se o provedor já recebeu a tarefa, o custo fica registrado (RN-08)."""
    with transaction.atomic():
        task = (
            creation.tasks.select_for_update()
            .filter(globalid=task_id, kind=ProviderTask.Kind.IMAGE_EDIT)
            .first()
        )
        if task is None:
            raise ResourceNotFound("Edição não encontrada.")
        if task.status not in TASK_ACTIVE:
            return task
        already_sent = task.status != ProviderTask.Status.QUEUED
        task.status = ProviderTask.Status.CANCELLED
        task.finished_at = timezone.now()
        task.save(update_fields=["status", "finished_at", "updated_at"])
        if already_sent:
            quota.consume(task)
        else:
            quota.release(task)
    return task


def apply_version(*, actor, creation: Creation, version_id, request_id: str = "") -> Creation:
    """Concluir a edição: a versão escolhida vira a atual. Itens no carrinho mantêm a sua."""
    from audit.services import record_event

    version = creation.versions.filter(globalid=version_id).first()
    if version is None:
        raise ResourceNotFound("Versão não encontrada.")
    if creation.status != Creation.Status.READY:
        raise GuardFailed("Esta criação não pode ser alterada agora.", code="not_editable")
    if creation.current_version_id == version.pk:
        return creation

    with transaction.atomic():
        creation.current_version = version
        creation.save(update_fields=["current_version", "updated_at"])
        record_event(
            instance=creation,
            event="version_applied",
            actor=actor,
            request_id=request_id,
            payload={"version": version.number},
        )
    creation.refresh_from_db()
    return creation


def delete_creation(*, actor, creation: Creation, request_id: str = "") -> None:
    from audit.services import record_event

    creation.deleted_at = timezone.now()
    creation.save(update_fields=["deleted_at", "updated_at"])
    record_event(instance=creation, event="deleted", actor=actor, request_id=request_id)


def delete_all_for_user(user) -> None:
    now = timezone.now()
    for creation in Creation.objects.filter(user=user, deleted_at__isnull=True):
        creation.deleted_at = now
        creation.save(update_fields=["deleted_at", "updated_at"])


def transfer_visitor_creations(*, visitor, user) -> int:
    return Creation.objects.filter(visitor=visitor, user__isnull=True).update(user=user)


def plain_background(png: bytes) -> bool:
    image = Image.open(io.BytesIO(png)).convert("RGB")
    width, height = image.size
    strip = max(1, int(min(width, height) * _BACKGROUND_STRIP_RATIO))
    boxes = [
        (0, 0, width, strip),
        (0, height - strip, width, height),
        (0, 0, strip, height),
        (width - strip, 0, width, height),
    ]
    for box in boxes:
        stat = ImageStat.Stat(image.crop(box))
        if min(stat.median) < _BACKGROUND_MIN_MEDIAN or max(stat.stddev) > _BACKGROUND_MAX_STDDEV:
            return False
    return True


def purge_expired_assets() -> dict:
    """Aplica a retenção. Arquivos ligados a um pedido nunca são apagados (RN-28)."""
    from accounts.models import Visitor
    from orders.models import OrderItem

    now = timezone.now()
    business = settings.BUSINESS
    purged = {"photos": 0, "generated": 0, "visitors": 0}
    with_order = OrderItem.objects.values("creation_id")

    photo_cutoff = now - timedelta(days=business["PHOTO_RETENTION_DAYS"])
    photos = CreationInput.objects.filter(
        photo__isnull=False, photo__purged_at__isnull=True, creation__created_at__lt=photo_cutoff
    ).exclude(creation_id__in=with_order)
    for source in photos.select_related("photo"):
        media.purge(source.photo)
        purged["photos"] += 1

    deleted_cutoff = now - timedelta(days=business["DELETED_CREATION_PURGE_DAYS"])
    deleted = Creation.objects.filter(deleted_at__lt=deleted_cutoff).exclude(pk__in=with_order)
    for creation in deleted.prefetch_related("versions__asset"):
        assets = [v.asset for v in creation.versions.all()]
        source = getattr(creation, "input", None)
        if source is not None and source.photo is not None:
            assets.append(source.photo)
        for asset in assets:
            if asset.purged_at is None:
                media.purge(asset)
                purged["generated"] += 1

    visitor_cutoff = now - timedelta(days=business["VISITOR_RETENTION_DAYS"])
    inactive = Visitor.objects.filter(last_seen_at__lt=visitor_cutoff)
    purged["visitors"] = inactive.count()
    # Sem dono, a criação some do produto: entra na retenção de excluídas.
    Creation.objects.filter(
        visitor__in=inactive, user__isnull=True, deleted_at__isnull=True
    ).update(deleted_at=now)
    inactive.delete()
    return purged
