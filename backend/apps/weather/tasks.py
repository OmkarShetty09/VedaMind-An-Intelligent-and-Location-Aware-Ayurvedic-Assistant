from celery import shared_task

from .cache import get_weather
from .models import GeoLocation


@shared_task
def refresh_weather_sweep():
    """Hourly beat task: refresh cached weather for active users' locations."""
    refreshed = 0
    for geo in GeoLocation.objects.select_related("user").filter(user__is_active=True).iterator():
        try:
            get_weather(geo.lat, geo.lon)
            refreshed += 1
        except Exception:
            continue
    return {"refreshed": refreshed}
