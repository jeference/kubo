"""Cobrança PIX, liquidação e reembolso. O pedido só é confirmado pelo gateway (RN-20)."""

from __future__ import annotations

from datetime import timedelta

import structlog
from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from audit.services import record_event
from common.alerts import alert
from common.exceptions import Conflict, DomainError
from common.fsm import apply_transition
from fulfillment import services as fulfillment
from integrations.ports import get_payment_gateway_port
from orders import services as orders
from orders.models import Order
from payments.fsm import CHARGE_FSM
from payments.models import Charge, LedgerEntry, WebhookEvent

log = structlog.get_logger(__name__)

_REFUNDABLE_ORDER_STATUSES = (
    Order.Status.PAID,
    Order.Status.IN_PRODUCTION,
    Order.Status.SHIPPED,
    Order.Status.DELIVERED,
)
_RECONCILE_MIN_AGE = timedelta(minutes=2)


def can_renew_payment(order: Order) -> bool:
    if order.status != Order.Status.EXPIRED or order.expired_at is None:
        return False
    window = timedelta(hours=settings.BUSINESS["PIX_RENEWAL_WINDOW_HOURS"])
    return timezone.now() - order.expired_at <= window


def pay_order(*, order: Order, actor=None, request_id: str = "") -> Charge:
    """Reaproveita o PIX pendente ou cria um novo. Bloqueia o pedido para não duplicar."""
    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)
        if locked.status == Order.Status.EXPIRED:
            if not can_renew_payment(locked):
                raise Conflict(
                    "Este pedido expirou. Refaça a compra pelo carrinho.", code="order_too_old"
                )
            orders.transition_order(
                order=locked, event="renew_payment", actor=actor, request_id=request_id
            )
            locked.expired_at = None
            locked.status = Order.Status.PENDING_PAYMENT
            locked.save(update_fields=["expired_at", "updated_at"])
        elif locked.status != Order.Status.PENDING_PAYMENT:
            raise Conflict("Este pedido já foi pago.", code="order_not_payable")

        pending = (
            locked.charges.filter(status=Charge.Status.PENDING, expires_at__gt=timezone.now())
            .order_by("-created_at")
            .first()
        )
        if pending is not None:
            return pending

        port = get_payment_gateway_port()
        seconds = settings.BUSINESS["PIX_EXPIRES_SECONDS"]
        gateway = port.create_charge(
            amount=locked.total_cents,
            reference=str(locked.globalid),
            description=f"Pedido Kubo {locked.number}",
            expires_in_seconds=seconds,
        )
        charge = Charge.objects.create(
            order=locked,
            provider=port.provider,
            external_id=gateway.external_id,
            amount_cents=locked.total_cents,
            pix_br_code=gateway.pix_br_code,
            pix_qr_base64=gateway.pix_qr_base64,
            expires_at=gateway.expires_at or timezone.now() + timedelta(seconds=seconds),
        )
        record_event(
            instance=charge, event="created", to_state=charge.status, request_id=request_id
        )
    return charge


def _post_revenue(*, order: Order, charge: Charge) -> None:
    LedgerEntry.objects.create(
        order=order,
        charge=charge,
        kind=LedgerEntry.Kind.PRODUCT_REVENUE,
        debit_account=LedgerEntry.Account.CUSTOMER,
        credit_account=LedgerEntry.Account.PLATFORM,
        amount_cents=order.subtotal_cents,
    )
    LedgerEntry.objects.create(
        order=order,
        charge=charge,
        kind=LedgerEntry.Kind.SHIPPING_COLLECTED,
        debit_account=LedgerEntry.Account.CUSTOMER,
        credit_account=LedgerEntry.Account.SHIPPING,
        amount_cents=order.shipping_cents,
    )


def on_charge_paid(*, charge: Charge, request_id: str = "") -> None:
    """Idempotente: confirmar de novo uma cobrança paga não tem efeito."""
    with transaction.atomic():
        locked = Charge.objects.select_for_update().get(pk=charge.pk)
        if locked.status == Charge.Status.PAID:
            return
        if locked.status == Charge.Status.REFUNDED:
            alert("payment_after_refund", charge_id=str(locked.globalid))
            return
        order = Order.objects.select_for_update().get(pk=locked.order_id)

        def mark_paid():
            locked.paid_at = timezone.now()
            locked.save(update_fields=["paid_at", "updated_at"])

        apply_transition(
            instance=locked,
            fsm=CHARGE_FSM,
            event="pay",
            request_id=request_id,
            effects=mark_paid,
        )

        if order.status in (Order.Status.PENDING_PAYMENT, Order.Status.EXPIRED):
            late = order.status == Order.Status.EXPIRED
            if late:
                alert("payment_after_expiry", order_id=str(order.globalid))
            _post_revenue(order=order, charge=locked)

            def effects():
                order.paid_at = timezone.now()
                order.expired_at = None
                order.save(update_fields=["paid_at", "expired_at", "updated_at"])
                fulfillment.create_jobs_for_order(order)
                orders.clear_paid_items_from_cart(order)

            orders.transition_order(
                order=order,
                event="pay_late" if late else "pay",
                request_id=request_id,
                effects=effects,
            )
            transaction.on_commit(lambda: orders.send_order_confirmed(order))
        else:
            # Segundo PIX pago: a cobrança fica paga, sem receita, e alguém devolve o excedente.
            alert(
                "duplicate_payment",
                order_id=str(order.globalid),
                charge_id=str(locked.globalid),
            )


def on_charge_refunded(*, charge: Charge, request_id: str = "") -> None:
    """Reembolso feito no painel do gateway. Registra o estorno e encerra o pedido."""
    with transaction.atomic():
        locked = Charge.objects.select_for_update().get(pk=charge.pk)
        if locked.status == Charge.Status.REFUNDED:
            return
        had_revenue = locked.ledger.filter(kind=LedgerEntry.Kind.PRODUCT_REVENUE).exists()
        apply_transition(instance=locked, fsm=CHARGE_FSM, event="refund", request_id=request_id)
        if not had_revenue:
            return  # Devolução de um PIX duplicado: o pedido segue normalmente.
        order = Order.objects.select_for_update().get(pk=locked.order_id)
        LedgerEntry.objects.create(
            order=order,
            charge=locked,
            kind=LedgerEntry.Kind.REFUND,
            debit_account=LedgerEntry.Account.PLATFORM,
            credit_account=LedgerEntry.Account.CUSTOMER,
            amount_cents=locked.amount_cents,
        )
        if order.status in _REFUNDABLE_ORDER_STATUSES:

            def effects():
                order.refunded_at = timezone.now()
                order.save(update_fields=["refunded_at", "updated_at"])
                fulfillment.cancel_jobs_for_order(order)

            orders.transition_order(
                order=order, event="refund", request_id=request_id, effects=effects
            )


def on_charge_disputed(*, charge: Charge, request_id: str = "") -> None:
    Charge.objects.filter(pk=charge.pk).update(disputed_at=timezone.now())
    record_event(instance=charge, event="disputed", request_id=request_id)
    alert("payment_disputed", charge_id=str(charge.globalid))


def expire_pending_charges() -> int:
    """Antes de expirar, confere o gateway: o pagamento pode ter chegado sem o webhook."""
    now = timezone.now()
    count = 0
    port = get_payment_gateway_port()
    for charge in Charge.objects.filter(status=Charge.Status.PENDING, expires_at__lte=now):
        try:
            status = port.get_charge_status(external_id=charge.external_id)
        except DomainError:
            continue  # Gateway fora: tenta na próxima rodada.
        if status == "paid":
            on_charge_paid(charge=charge)
            continue
        with transaction.atomic():
            apply_transition(instance=charge, fsm=CHARGE_FSM, event="expire")
            order = Order.objects.select_for_update().get(pk=charge.order_id)
            other_pending = order.charges.filter(status=Charge.Status.PENDING).exists()
            if order.status == Order.Status.PENDING_PAYMENT and not other_pending:

                def effects(order=order):
                    order.expired_at = timezone.now()
                    order.save(update_fields=["expired_at", "updated_at"])

                orders.transition_order(order=order, event="expire", effects=effects)
        count += 1
    return count


def reconcile_pending_charges() -> int:
    """Cobre webhooks perdidos."""
    port = get_payment_gateway_port()
    cutoff = timezone.now() - _RECONCILE_MIN_AGE
    count = 0
    for charge in Charge.objects.filter(status=Charge.Status.PENDING, created_at__lte=cutoff):
        try:
            status = port.get_charge_status(external_id=charge.external_id)
        except DomainError:
            continue
        if status == "paid":
            on_charge_paid(charge=charge)
            count += 1
    return count


# --- Webhook ---

_PAID_EVENTS = {"transparent.completed"}
_REFUND_EVENTS = {"transparent.refunded"}
_DISPUTE_EVENTS = {"transparent.disputed"}


def _candidate_refs(data: dict) -> list[str]:
    """O id da cobrança no evento: coletamos os candidatos, e o banco decide por igualdade."""
    if not isinstance(data, dict):
        return []
    nested = (value.get("id") for value in data.values() if isinstance(value, dict))
    return [str(value) for value in (data.get("id"), *nested) if isinstance(value, str) and value]


def ingest_gateway_event(*, provider: str, payload: dict, request_id: str = "") -> None:
    """Registra e processa. Evento repetido não tem efeito, salvo se a tentativa anterior falhou.

    O reenvio manual pelo painel do gateway usa um novo `id`: por isso o status da cobrança
    também protege contra efeitos duplicados.
    """
    refs = _candidate_refs(payload.get("data") or {})
    kind = str(payload.get("event", ""))
    event_id = str(payload.get("id") or f"{kind}:{refs[0] if refs else 'sem-id'}")
    try:
        with transaction.atomic():
            event = WebhookEvent.objects.create(
                provider=provider, event_id=event_id, event_kind=kind, payload=payload
            )
    except IntegrityError:
        event = WebhookEvent.objects.get(provider=provider, event_id=event_id)
        if event.status != WebhookEvent.Status.FAILED:
            return
    _process(event=event, kind=kind, refs=refs, request_id=request_id)


def _mark(event: WebhookEvent, status: str, error: str = "") -> None:
    event.status = status
    event.error = error
    event.processed_at = timezone.now()
    event.save(update_fields=["status", "error", "processed_at", "updated_at"])


def _process(*, event: WebhookEvent, kind: str, refs: list[str], request_id: str) -> None:
    if kind not in _PAID_EVENTS | _REFUND_EVENTS | _DISPUTE_EVENTS:
        log.warning("webhook_unhandled_event", event_kind=kind)
        _mark(event, WebhookEvent.Status.PROCESSED)
        return
    charge = Charge.objects.filter(external_id__in=refs).first() if refs else None
    if charge is None:
        _mark(event, WebhookEvent.Status.FAILED, "cobrança não encontrada")
        alert("payment_webhook_unmatched", event_kind=kind, event_id=event.event_id)
        return
    try:
        if kind in _PAID_EVENTS:
            # Nunca liquida só pelo nome do evento: confere no gateway. Gateway fora vira 502.
            status = get_payment_gateway_port().get_charge_status(external_id=charge.external_id)
            if status != "paid":
                _mark(event, WebhookEvent.Status.FAILED, f"gateway informou {status}")
                return
            on_charge_paid(charge=charge, request_id=request_id)
        elif kind in _REFUND_EVENTS:
            on_charge_refunded(charge=charge, request_id=request_id)
        else:
            on_charge_disputed(charge=charge, request_id=request_id)
    except DomainError as exc:
        _mark(event, WebhookEvent.Status.FAILED, exc.detail)
        if exc.status_code >= 500:
            raise
        alert("payment_webhook_failed", event_id=event.event_id, error=exc.detail)
        return
    _mark(event, WebhookEvent.Status.PROCESSED)
