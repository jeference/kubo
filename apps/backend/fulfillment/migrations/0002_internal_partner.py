from django.conf import settings
from django.db import migrations


def seed(apps, schema_editor):
    apps.get_model("fulfillment", "Partner").objects.create(
        name="Kubo",
        origin_postal_code=settings.INTERNAL_PARTNER_POSTAL_CODE,
        is_internal=True,
    )


class Migration(migrations.Migration):
    dependencies = [("fulfillment", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
