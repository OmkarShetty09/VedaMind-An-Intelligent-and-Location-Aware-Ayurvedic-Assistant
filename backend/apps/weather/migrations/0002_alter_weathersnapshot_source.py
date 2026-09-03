from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weathersnapshot',
            name='source',
            field=models.CharField(default='open-meteo', max_length=16),
        ),
    ]
