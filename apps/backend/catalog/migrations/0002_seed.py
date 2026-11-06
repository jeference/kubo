"""Dados iniciais: tamanhos e preços (RN-11) e filamentos."""

from django.db import migrations

# código, rótulo, maior lado (mm), preço, peso da embalagem (g), L, A, C (cm), padrão, ordem
_SIZES = [
    ("4cm", "4 cm Mini", 40, 5990, 100, 10, 8, 10, False, 0),
    ("6cm", "6 cm Ideal", 60, 9990, 150, 12, 10, 12, True, 1),
    ("8cm", "8 cm Grande", 80, 14490, 220, 14, 12, 14, False, 2),
    ("10cm", "10 cm Destaque", 100, 18990, 320, 16, 14, 16, False, 3),
    ("12cm", "12 cm Exposição", 120, 22990, 450, 18, 16, 18, False, 4),
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
    filament_model = apps.get_model("catalog", "Filament")
    for name, hex_code in _FILAMENTS:
        filament_model.objects.create(name=name, hex_code=hex_code)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
