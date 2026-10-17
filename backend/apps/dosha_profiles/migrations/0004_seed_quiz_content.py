"""Initial quiz questions and dosha descriptions (from data/quiz.json); edit them in the admin afterwards."""

import json
from pathlib import Path

from django.db import migrations

DATA = Path(__file__).resolve().parents[1] / "data" / "quiz.json"


def load(apps, schema_editor):
    DoshaInfo = apps.get_model("dosha_profiles", "DoshaInfo")
    QuizQuestion = apps.get_model("dosha_profiles", "QuizQuestion")
    content = json.loads(DATA.read_text(encoding="utf-8"))
    for item in content["doshas"]:
        DoshaInfo.objects.update_or_create(dosha=item["dosha"], defaults={k: v for k, v in item.items() if k != "dosha"})
    for order, q in enumerate(content["questions"]):
        QuizQuestion.objects.update_or_create(
            key=q["key"], defaults={"section": q["section"], "prompt": q["prompt"], "options": q["options"], "order": order}
        )


def unload(apps, schema_editor):
    apps.get_model("dosha_profiles", "QuizQuestion").objects.all().delete()
    apps.get_model("dosha_profiles", "DoshaInfo").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("dosha_profiles", "0003_quiz_content")]
    operations = [migrations.RunPython(load, unload)]
