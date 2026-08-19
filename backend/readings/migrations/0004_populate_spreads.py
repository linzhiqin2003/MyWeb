from django.db import migrations


def populate_spreads(apps, schema_editor):
    from readings.management.commands.populate_spreads import SPREADS

    Spread = apps.get_model("readings", "Spread")
    for spread_data in SPREADS:
        defaults = {k: v for k, v in spread_data.items() if k != "name"}
        Spread.objects.update_or_create(name=spread_data["name"], defaults=defaults)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("readings", "0003_spread_depth_fields"),
    ]

    operations = [
        migrations.RunPython(populate_spreads, noop),
    ]
