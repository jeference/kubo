"""Dinheiro: só este módulo escreve aqui. Valores em centavos inteiros."""

from django.db import models

from common.models import AppendOnlyModel, BaseModel


class Charge(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        PAID = "paid", "Paga"
        EXPIRED = "expired", "Expirada"
        FAILED = "failed", "Falhou"
        REFUNDED = "refunded", "Reembolsada"

    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="charges")
    provider = models.CharField(max_length=32)
    external_id = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    amount_cents = models.PositiveIntegerField()
    pix_br_code = models.TextField(blank=True)
    pix_qr_base64 = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    disputed_at = models.DateTimeField(null=True, blank=True)


class WebhookEvent(BaseModel):
    class Status(models.TextChoices):
        RECEIVED = "received", "Recebido"
        PROCESSED = "processed", "Processado"
        FAILED = "failed", "Falhou"

    provider = models.CharField(max_length=32)
    event_id = models.CharField(max_length=128)
    event_kind = models.CharField(max_length=64, blank=True)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.RECEIVED)
    error = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=["provider", "event_id"], name="webhook_event_uq")
        ]


class LedgerEntry(AppendOnlyModel):
    """Lançamentos imutáveis. Correção é lançamento compensatório; saldos são derivados."""

    class Kind(models.TextChoices):
        PRODUCT_REVENUE = "product_revenue", "Receita de produto"
        SHIPPING_COLLECTED = "shipping_collected", "Frete recebido"
        REFUND = "refund", "Reembolso"
        PARTNER_PAYABLE = "partner_payable", "A pagar ao parceiro"

    class Account(models.TextChoices):
        CUSTOMER = "customer", "Cliente"
        PLATFORM = "platform", "Plataforma"
        SHIPPING = "shipping", "Frete a repassar"
        PARTNER = "partner", "Parceiro"

    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="ledger")
    charge = models.ForeignKey(Charge, on_delete=models.PROTECT, related_name="ledger")
    kind = models.CharField(max_length=24, choices=Kind.choices)
    debit_account = models.CharField(max_length=16, choices=Account.choices)
    credit_account = models.CharField(max_length=16, choices=Account.choices)
    amount_cents = models.PositiveIntegerField()

    class Meta(AppendOnlyModel.Meta):
        constraints = [models.UniqueConstraint(fields=["charge", "kind"], name="ledger_charge_uq")]
