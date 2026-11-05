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


class CostParameters(BaseModel):
    """Parâmetros da estimativa de custo. Nunca são editados: cada mudança é uma nova versão,
    para comparar o estimado com o custo real de cada modelo."""

    version = models.PositiveIntegerField(unique=True)
    density_g_cm3 = models.DecimalField(max_digits=5, decimal_places=3)
    wall_mm = models.DecimalField(max_digits=5, decimal_places=2)
    infill_fraction = models.DecimalField(max_digits=4, decimal_places=3)
    cost_per_gram_cents = models.DecimalField(max_digits=8, decimal_places=2)
    cost_per_hour_cents = models.DecimalField(max_digits=8, decimal_places=2)
    grams_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    purge_grams = models.DecimalField(max_digits=6, decimal_places=2)
    packaging_cents = models.PositiveIntegerField()
    gateway_fee_fraction = models.DecimalField(max_digits=5, decimal_places=4)
    min_margin_fraction = models.DecimalField(max_digits=4, decimal_places=3)

    class Meta(BaseModel.Meta):
        ordering = ["-version"]


class Filament(BaseModel):
    """Preparação: hoje as cores só orientam os prompts (catalog/prompts.py)."""

    name = models.CharField(max_length=40, unique=True)
    hex_code = models.CharField(max_length=7)
    brand = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
