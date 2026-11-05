from django.db import models

from common.models import BaseModel


class ShippingQuote(BaseModel):
    """Uma opção de frete cotada, válida por pouco tempo."""

    actor_key = models.CharField(max_length=32)
    origin_postal_code = models.CharField(max_length=8)
    destination_postal_code = models.CharField(max_length=8)
    service_id = models.CharField(max_length=32)
    service_name = models.CharField(max_length=64)
    company = models.CharField(max_length=64, blank=True)
    price_cents = models.PositiveIntegerField()
    shipping_days = models.PositiveSmallIntegerField()
    delivery_days = models.PositiveSmallIntegerField()
    item_ids = models.JSONField(default=list)
    expires_at = models.DateTimeField()
