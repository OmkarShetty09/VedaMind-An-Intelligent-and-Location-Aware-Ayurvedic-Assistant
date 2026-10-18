from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("conversations", "0004_seed_chat_suggestions")]

    operations = [
        migrations.AddField(
            model_name="message",
            name="cautions",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
