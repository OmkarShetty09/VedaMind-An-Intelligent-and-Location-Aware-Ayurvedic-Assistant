import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("vedamind")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
# The beat schedule is CELERY_BEAT_SCHEDULE in settings (intervals come from .env).
