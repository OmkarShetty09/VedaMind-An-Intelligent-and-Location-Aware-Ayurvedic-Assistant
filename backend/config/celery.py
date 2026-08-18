import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("vedamind")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "weather-refresh-sweep": {
        "task": "apps.weather.tasks.refresh_weather_sweep",
        "schedule": 3600.0,
    },
    "guardrail-daily-digest": {
        "task": "apps.interactions_log.tasks.daily_digest",
        "schedule": 86400.0,
    },
}
