"""Dados iniciais. Preços e parâmetros de custo são [Proposta]: a tabela de preços veio do
protótipo como exemplo e precisa ser substituída antes do lançamento (PRD, RN-11)."""

from decimal import Decimal

from django.db import migrations

# código, rótulo, maior lado (mm), preço, peso da embalagem (g), L, A, C (cm), padrão, ordem
_SIZES = [
    ("6cm", "6 cm Ideal", 60, 12990, 150, 12, 10, 12, True, 0),
    ("4cm", "4 cm Mini", 40, 5990, 100, 10, 8, 10, False, 1),
    ("5cm", "5 cm Pequeno", 50, 8990, 120, 11, 9, 11, False, 2),
    ("7cm", "7 cm Médio", 70, 17990, 180, 13, 11, 13, False, 3),
    ("8cm", "8 cm Grande", 80, 22990, 220, 14, 12, 14, False, 4),
    ("10cm", "10 cm Destaque", 100, 29990, 320, 16, 14, 16, False, 5),
    ("12cm", "12 cm Exposição", 120, 59990, 450, 18, 16, 18, False, 6),
    ("15cm", "15 cm Peça central", 150, 79990, 700, 22, 20, 22, False, 7),
]
_FILAMENTS = [
    ("white", "#FFFFFF"),
    ("black", "#000000"),
    ("gray", "#8E9089"),
    ("red", "#C12E1F"),
    ("orange", "#FF6A13"),
    ("yellow", "#F4EE2A"),
    ("green", "#00AE42"),
    ("blue", "#0A2989"),
    ("purple", "#5E43B7"),
    ("pink", "#F5547C"),
    ("brown", "#9D432C"),
    ("beige", "#F7E6DE"),
    ("light skin", "#EBC8B0"),
]


def seed(apps, schema_editor):
    size_model = apps.get_model("catalog", "ProductSize")
    for code, label, mm, price, grams, width, height, length, default, order in _SIZES:
        size_model.objects.create(
            code=code,
            label=label,
            longest_side_mm=mm,
            price_cents=price,
            package_weight_grams=grams,
            package_width_cm=width,
            package_height_cm=height,
            package_length_cm=length,
            is_default=default,
            sort_order=order,
        )
    apps.get_model("catalog", "CostParameters").objects.create(
        version=1,
        density_g_cm3=Decimal("1.240"),
        wall_mm=Decimal("1.20"),
        infill_fraction=Decimal("0.150"),
        cost_per_gram_cents=Decimal("15.00"),
        cost_per_hour_cents=Decimal("500.00"),
        grams_per_hour=Decimal("15.00"),
        purge_grams=Decimal("30.00"),
        packaging_cents=500,
        gateway_fee_fraction=Decimal("0.0200"),
        min_margin_fraction=Decimal("0.250"),
    )
    filament_model = apps.get_model("catalog", "Filament")
    for name, hex_code in _FILAMENTS:
        filament_model.objects.create(name=name, hex_code=hex_code)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
