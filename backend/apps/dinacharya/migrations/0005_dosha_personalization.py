from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("dinacharya", "0004_season_choices_from_calendar")]

    operations = [
        migrations.AddField(
            model_name="routineactivity",
            name="personalized",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="routinetemplate",
            name="dosha_tips",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="routinetemplate",
            name="doshas",
            field=models.JSONField(blank=True, default=list, help_text='Only for these doshas, e.g. ["kapha"]. Empty = all.'),
        ),
    ]
