from django.db import migrations

INITIAL = [
    "What should my morning routine look like?",
    "Tell me about Ashwagandha",
    "What is Dinacharya?",
    "How does Ayurveda describe seasonal living?",
]


def load(apps, schema_editor):
    ChatSuggestion = apps.get_model("conversations", "ChatSuggestion")
    for order, text in enumerate(INITIAL):
        ChatSuggestion.objects.get_or_create(text=text, defaults={"order": order})


def unload(apps, schema_editor):
    apps.get_model("conversations", "ChatSuggestion").objects.filter(text__in=INITIAL).delete()


class Migration(migrations.Migration):
    dependencies = [("conversations", "0003_chat_suggestion")]
    operations = [migrations.RunPython(load, unload)]
