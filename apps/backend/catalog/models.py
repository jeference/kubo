from django.db import models

from common.models import BaseModel


class ProductSize(BaseModel):
    """Tamanho vendido. `longest_side_mm` é a maior dimensão da peça (RN-12)."""

    code = models.CharField(max_length=16, unique=True)
    label = models.CharField(max_length=40)
    longest_side_mm = models.PositiveIntegerField()
    price_cents = models.PositiveIntegerField()
    package_weight_grams = models.PositiveIntegerField()
    package_width_cm = models.PositiveSmallIntegerField()
    package_height_cm = models.PositiveSmallIntegerField()
    package_length_cm = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta(BaseModel.Meta):
        ordering = ["sort_order"]


class Filament(BaseModel):
    """Preparação: hoje as cores só orientam os prompts (catalog/prompts.py)."""

    name = models.CharField(max_length=40, unique=True)
    hex_code = models.CharField(max_length=7)
    brand = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
