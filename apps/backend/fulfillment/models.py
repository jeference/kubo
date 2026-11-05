"""Terreno para o app de parceiros. Neste app, só o pagamento cria `ProductionJob`.

O cliente nunca vê quem produziu a peça. O parceiro, quando existir, não verá e-mail nem CPF.
"""

from django.conf import settings
from django.db import models

from common.models import BaseModel


class Partner(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Ativo"
        INACTIVE = "inactive", "Inativo"

    name = models.CharField(max_length=120)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    origin_postal_code = models.CharField(max_length=8)
    is_internal = models.BooleanField(default=False)


class PartnerMember(BaseModel):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="partner_memberships"
    )

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=["partner", "user"], name="partner_member_uq")
        ]


class ProductionJob(BaseModel):
    class Status(models.TextChoices):
        UNASSIGNED = "unassigned", "Sem parceiro"
        ASSIGNED = "assigned", "Atribuída"
        IN_PRODUCTION = "in_production", "Em produção"
        READY_TO_SHIP = "ready_to_ship", "Pronta para envio"
        SHIPPED = "shipped", "Enviada"
        CANCELLED = "cancelled", "Cancelada"

    order_item = models.OneToOneField(
        "orders.OrderItem", on_delete=models.PROTECT, related_name="production_job"
    )
    partner = models.ForeignKey(
        Partner, null=True, blank=True, on_delete=models.PROTECT, related_name="jobs"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.UNASSIGNED)
    assigned_at = models.DateTimeField(null=True, blank=True)


class ProductionFile(BaseModel):
    class Kind(models.TextChoices):
        GLB = "glb", "GLB"
        STL = "stl", "STL"
        THREE_MF = "3mf", "3MF"

    job = models.ForeignKey(ProductionJob, on_delete=models.CASCADE, related_name="files")
    kind = models.CharField(max_length=4, choices=Kind.choices)
    version = models.PositiveSmallIntegerField(default=1)
    asset = models.ForeignKey("media.Asset", on_delete=models.PROTECT, related_name="+")


class Shipment(BaseModel):
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="shipments")
    partner = models.ForeignKey(
        Partner, null=True, blank=True, on_delete=models.PROTECT, related_name="shipments"
    )
    carrier = models.CharField(max_length=64, blank=True)
    tracking_code = models.CharField(max_length=64, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
