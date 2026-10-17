"""Initial Dinacharya activity templates (from data/routine_templates.json); edit them in the admin afterwards."""

import json
from pathlib import Path

from django.db import migrations

DATA = Path(__file__).resolve().parents[1] / "data" / "routine_templates.json"
FIELDS = ("order", "time_of_day", "start", "end", "title", "description", "reasons", "citations", "dosha_target",
          "above_temperature_c", "season_overrides", "dosha_overrides")


def load(apps, schema_editor):
    RoutineTemplate = apps.get_model("dinacharya", "RoutineTemplate")
    for item in json.loads(DATA.read_text(encoding="utf-8"))["templates"]:
        defaults = {f: item[f] for f in FIELDS if f in item}
        RoutineTemplate.objects.update_or_create(key=item["key"], defaults=defaults)


def unload(apps, schema_editor):
    apps.get_model("dinacharya", "RoutineTemplate").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("dinacharya", "0002_routine_template")]
    operations = [migrations.RunPython(load, unload)]
