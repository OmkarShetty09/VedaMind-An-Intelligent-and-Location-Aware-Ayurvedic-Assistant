import uuid

from django.conf import settings
from django.db import models


class WeatherSnapshot(models.Model):
    """Cached weather per location. 'source' records provenance honestly."""

    lat = models.FloatField(db_index=True)
    lon = models.FloatField()
    fetched_at = models.DateTimeField(db_index=True)
    payload = models.JSONField(default=dict)
    source = models.CharField(max_length=16, default="open-meteo")  # open-meteo | stale

    class Meta:
        indexes = [models.Index(fields=["lat", "lon", "fetched_at"])]

    def __str__(self):
        return f"{self.lat:.2f},{self.lon:.2f} @ {self.fetched_at:%Y-%m-%d %H:%M} ({self.source})"

    @property
    def temperature_c(self):
        return (self.payload.get("current") or {}).get("temp")

    @property
    def is_stale(self) -> bool:
        from datetime import timedelta

        from django.utils import timezone

        age = timezone.now() - self.fetched_at
        return age > timedelta(minutes=settings.WEATHER_CACHE_TTL_MINUTES)


class GeoLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="geo_location")
    lat = models.FloatField()
    lon = models.FloatField()
    accuracy = models.FloatField(default=0.0)  # meters; 0 = unknown
    source = models.CharField(max_length=16, default="gps")  # gps | ip | user | default
    confidence = models.FloatField(default=1.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id}: {self.lat},{self.lon} ({self.source})"
