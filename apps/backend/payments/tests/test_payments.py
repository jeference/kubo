from __future__ import annotations

from datetime import timedelta

from django.core.management import call_command
from django.db.models import Sum
from django.utils import timezone

from fulfillment.models import ProductionJob
from integrations.adapters.email_console import outbox
from integrations.adapters.stubs import stub_set_charge_status
from orders.models import Order
from orders.tests.helpers import place_order
from payments import services
from payments.models import Charge, LedgerEntry, WebhookEvent

SECRET = "segredo-teste"


def _pay(client, order):
    response = client.post(f"/api/orders/{order['id']}/pay/")
    assert response.status_code == 200, response.data
    return response.data["charge"]


def _webhook(anon, external_id, *, event="transparent.completed", event_id="evt_1"):
    return anon.post(
        f"/api/webhooks/abacatepay/?webhookSecret={SECRET}",
        {"id": event_id, "event": event, "data": {"id": external_id}},
        format="json",
    )


def _paid_order(client, anon, django_capture_on_commit_callbacks):
    order = place_order(client)
    charge = _pay(client, order)
    external = Charge.objects.get(globalid=charge["id"]).external_id
    stub_set_charge_status(external, "paid")
    with django_capture_on_commit_callbacks(execute=True):
        assert _webhook(anon, external).status_code == 200
    return Order.objects.get(globalid=order["id"]), external


def test_pay_reuses_pending_charge(visitor_client):
    order = place_order(visitor_client)
    first = _pay(visitor_client, order)
    second = _pay(visitor_client, order)
    assert first["id"] == second["id"]
    assert first["pix_br_code"]
    assert first["pix_qr_base64"].startswith("data:image/png;base64,")
    assert first["amount_cents"] == order["total_cents"]


def test_webhook_requires_secret(anon, visitor_client):
    response = anon.post(
        "/api/webhooks/abacatepay/?webhookSecret=errado",
        {"id": "x", "event": "transparent.completed", "data": {"id": "y"}},
        format="json",
    )
    assert response.status_code == 401
    assert WebhookEvent.objects.count() == 0


def test_browser_cannot_confirm_payment(visitor_client):
    """Sem webhook conferido no gateway, o pedido continua aguardando (RN-20)."""
    order = place_order(visitor_client)
    charge = _pay(visitor_client, order)
    external = Charge.objects.get(globalid=charge["id"]).external_id
    response = _webhook(visitor_client, external)  # Gateway ainda diz pendente.
    assert response.status_code == 200
    assert Order.objects.get(globalid=order["id"]).status == Order.Status.PENDING_PAYMENT
    assert WebhookEvent.objects.get().status == WebhookEvent.Status.FAILED


def test_paid_webhook_settles_order(visitor_client, anon, django_capture_on_commit_callbacks):
    outbox.clear()
    order, _ = _paid_order(visitor_client, anon, django_capture_on_commit_callbacks)
    assert order.status == Order.Status.PAID
    assert order.paid_at is not None
    entries = LedgerEntry.objects.filter(order=order)
    assert entries.count() == 2
    assert entries.aggregate(total=Sum("amount_cents"))["total"] == order.total_cents
    assert ProductionJob.objects.filter(order_item__order=order).count() == 1
    job = ProductionJob.objects.get(order_item__order=order)
    assert job.status == ProductionJob.Status.UNASSIGNED
    assert job.partner is None
    assert visitor_client.get("/api/cart/").data["item_count"] == 0
    assert any("/acompanhar/" in mail["body"] for mail in outbox)


def test_webhook_is_idempotent(visitor_client, anon, django_capture_on_commit_callbacks):
    order, external = _paid_order(visitor_client, anon, django_capture_on_commit_callbacks)
    assert _webhook(anon, external).status_code == 200  # Mesmo id.
    assert _webhook(anon, external, event_id="evt_reenvio").status_code == 200  # Id novo.
    assert LedgerEntry.objects.filter(order=order).count() == 2
    assert ProductionJob.objects.filter(order_item__order=order).count() == 1


def test_unmatched_webhook_returns_200_and_records_failure(anon):
    assert _webhook(anon, "desconhecido").status_code == 200
    assert WebhookEvent.objects.get().status == WebhookEvent.Status.FAILED


def test_unknown_event_returns_200(anon):
    response = _webhook(anon, "x", event="subscription.renewed")
    assert response.status_code == 200
    assert WebhookEvent.objects.get().status == WebhookEvent.Status.PROCESSED


def test_gateway_down_returns_502_for_redelivery(visitor_client, anon, monkeypatch):
    from common.exceptions import UpstreamUnavailable

    order = place_order(visitor_client)
    charge = _pay(visitor_client, order)
    external = Charge.objects.get(globalid=charge["id"]).external_id

    class Down:
        def get_charge_status(self, *, external_id):
            raise UpstreamUnavailable()

    monkeypatch.setattr("payments.services.get_payment_gateway_port", lambda: Down())
    assert _webhook(anon, external).status_code == 502
    monkeypatch.undo()
    stub_set_charge_status(external, "paid")
    assert _webhook(anon, external).status_code == 200  # A nova entrega reprocessa.
    assert Order.objects.get(globalid=order["id"]).status == Order.Status.PAID


def test_expire_and_renew_payment(visitor_client):
    order = place_order(visitor_client)
    charge = _pay(visitor_client, order)
    Charge.objects.filter(globalid=charge["id"]).update(
        expires_at=timezone.now() - timedelta(minutes=1)
    )
    call_command("expire_pending_charges")
    detail = visitor_client.get(f"/api/orders/{order['id']}/").data
    assert detail["status"] == "expired"
    assert detail["can_renew_payment"] is True
    assert visitor_client.get("/api/cart/").data["item_count"] == 1  # RN-18

    renewed = visitor_client.post(f"/api/orders/{order['id']}/pay/").data
    assert renewed["status"] == "pending_payment"
    assert renewed["charge"]["id"] != charge["id"]
    assert renewed["charge"]["status"] == "pending"


def test_too_old_order_cannot_renew(visitor_client):
    order = place_order(visitor_client)
    charge = _pay(visitor_client, order)
    Charge.objects.filter(globalid=charge["id"]).update(
        expires_at=timezone.now() - timedelta(minutes=1)
    )
    call_command("expire_pending_charges")
    Order.objects.filter(globalid=order["id"]).update(expired_at=timezone.now() - timedelta(days=2))
    response = visitor_client.post(f"/api/orders/{order['id']}/pay/")
    assert response.status_code == 409
    assert response.data["code"] == "order_too_old"


def test_expire_checks_gateway_first(visitor_client):
    order = place_order(visitor_client)
    charge = _pay(visitor_client, order)
    db_charge = Charge.objects.get(globalid=charge["id"])
    stub_set_charge_status(db_charge.external_id, "paid")
    Charge.objects.filter(pk=db_charge.pk).update(expires_at=timezone.now() - timedelta(minutes=1))
    call_command("expire_pending_charges")
    assert Order.objects.get(globalid=order["id"]).status == Order.Status.PAID


def test_late_payment_after_expiry_settles(visitor_client, anon):
    order = place_order(visitor_client)
    charge = _pay(visitor_client, order)
    db_charge = Charge.objects.get(globalid=charge["id"])
    Charge.objects.filter(pk=db_charge.pk).update(expires_at=timezone.now() - timedelta(minutes=1))
    call_command("expire_pending_charges")
    stub_set_charge_status(db_charge.external_id, "paid")
    assert _webhook(anon, db_charge.external_id).status_code == 200
    assert Order.objects.get(globalid=order["id"]).status == Order.Status.PAID


def test_duplicate_pix_has_no_second_revenue(
    visitor_client, anon, django_capture_on_commit_callbacks
):
    order, first_external = _paid_order(visitor_client, anon, django_capture_on_commit_callbacks)
    second = Charge.objects.create(
        order=order,
        provider="stub",
        external_id="pix_stub_segundo",
        amount_cents=order.total_cents,
        expires_at=timezone.now() + timedelta(minutes=30),
    )
    stub_set_charge_status(second.external_id, "paid")
    assert _webhook(anon, second.external_id, event_id="evt_2").status_code == 200
    second.refresh_from_db()
    assert second.status == Charge.Status.PAID
    assert LedgerEntry.objects.filter(order=order).count() == 2
    # Devolver o PIX duplicado não encerra o pedido.
    assert (
        _webhook(
            anon, second.external_id, event="transparent.refunded", event_id="evt_3"
        ).status_code
        == 200
    )
    assert Order.objects.get(pk=order.pk).status == Order.Status.PAID


def test_refund_from_gateway_panel(visitor_client, anon, django_capture_on_commit_callbacks):
    order, external = _paid_order(visitor_client, anon, django_capture_on_commit_callbacks)
    outbox.clear()
    with django_capture_on_commit_callbacks(execute=True):
        response = _webhook(anon, external, event="transparent.refunded", event_id="evt_refund")
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == Order.Status.REFUNDED
    refund = LedgerEntry.objects.get(order=order, kind=LedgerEntry.Kind.REFUND)
    assert refund.amount_cents == order.total_cents
    assert ProductionJob.objects.get(order_item__order=order).status == (
        ProductionJob.Status.CANCELLED
    )
    assert any("Reembolsado" in mail["subject"] for mail in outbox)
    # Repetir não duplica.
    _webhook(anon, external, event="transparent.refunded", event_id="evt_refund_2")
    assert LedgerEntry.objects.filter(order=order, kind=LedgerEntry.Kind.REFUND).count() == 1


def test_dispute_only_flags(visitor_client, anon, django_capture_on_commit_callbacks):
    order, external = _paid_order(visitor_client, anon, django_capture_on_commit_callbacks)
    assert (
        _webhook(anon, external, event="transparent.disputed", event_id="evt_d").status_code == 200
    )
    assert Charge.objects.get(external_id=external).disputed_at is not None
    assert Order.objects.get(pk=order.pk).status == Order.Status.PAID


def test_ledger_is_append_only(visitor_client, anon, django_capture_on_commit_callbacks):
    import pytest

    from common.exceptions import ImmutableRecordError

    order, _ = _paid_order(visitor_client, anon, django_capture_on_commit_callbacks)
    entry = LedgerEntry.objects.filter(order=order).first()
    entry.amount_cents = 1
    with pytest.raises(ImmutableRecordError):
        entry.save()
    with pytest.raises(ImmutableRecordError):
        entry.delete()


def test_reconcile_covers_lost_webhook(visitor_client):
    order = place_order(visitor_client)
    charge = _pay(visitor_client, order)
    db_charge = Charge.objects.get(globalid=charge["id"])
    Charge.objects.filter(pk=db_charge.pk).update(created_at=timezone.now() - timedelta(minutes=5))
    assert services.reconcile_pending_charges() == 0
    stub_set_charge_status(db_charge.external_id, "paid")
    assert services.reconcile_pending_charges() == 1
    assert Order.objects.get(globalid=order["id"]).status == Order.Status.PAID
