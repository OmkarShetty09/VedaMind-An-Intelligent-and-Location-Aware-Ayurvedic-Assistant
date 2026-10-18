"""Re-seed the Dinacharya templates with the dosha-specific content (data/routine_templates.json)."""

import json
from pathlib import Path

from django.db import migrations

DATA = Path(__file__).resolve().parents[1] / "data" / "routine_templates.json"
FIELDS = ("order", "time_of_day", "start", "end", "title", "description", "reasons", "citations", "dosha_target",
          "above_temperature_c", "season_overrides", "dosha_overrides", "dosha_tips", "doshas")


def load(apps, schema_editor):
    RoutineTemplate = apps.get_model("dinacharya", "RoutineTemplate")
    for item in json.loads(DATA.read_text(encoding="utf-8"))["templates"]:
        defaults = {f: item.get(f, RoutineTemplate._meta.get_field(f).get_default()) for f in FIELDS}
        RoutineTemplate.objects.update_or_create(key=item["key"], defaults=defaults)


class Migration(migrations.Migration):
    dependencies = [("dinacharya", "0005_dosha_personalization")]
    operations = [migrations.RunPython(load, migrations.RunPython.noop)]
