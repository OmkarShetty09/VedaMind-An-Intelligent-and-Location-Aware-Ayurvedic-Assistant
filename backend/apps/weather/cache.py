"""Cache-first weather access with graceful degradation. Never fabricates data."""

import logging

from django.utils import timezone

from .clients import WeatherClientError, fetch_one_call
from .models import WeatherSnapshot

logger = logging.getLogger(__name__)


def get_weather(lat: float, lon: float) -> dict:
    """Return {payload, source, fetched_at}. Falls back to stale, then to none."""
    snapshot = WeatherSnapshot.objects.filter(lat=lat, lon=lon).order_by("-fetched_at").first()

    if snapshot and not snapshot.is_stale:
        return {"payload": snapshot.payload, "source": snapshot.source, "fetched_at": snapshot.fetched_at}

    if snapshot:
        try:
            fresh = _refresh(snapshot)
            return {"payload": fresh.payload, "source": fresh.source, "fetched_at": fresh.fetched_at}
        except WeatherClientError:
            logger.warning("Weather refresh failed; serving stale snapshot.")
            return {"payload": snapshot.payload, "source": "stale", "fetched_at": snapshot.fetched_at}

    try:
        data = fetch_one_call(lat, lon)
        snapshot = WeatherSnapshot.objects.create(
            lat=lat, lon=lon, payload=data,
            source="open-meteo", fetched_at=timezone.now(),
        )
        return {"payload": snapshot.payload, "source": snapshot.source, "fetched_at": snapshot.fetched_at}
    except WeatherClientError as exc:
        logger.warning("Weather unavailable: %s", exc)
        return {"payload": {}, "source": "unavailable", "fetched_at": None}


def _refresh(snapshot: WeatherSnapshot) -> WeatherSnapshot:
    data = fetch_one_call(snapshot.lat, snapshot.lon)
    snapshot.payload = data
    snapshot.source = "open-meteo"
    snapshot.fetched_at = timezone.now()
    snapshot.save(update_fields=["payload", "source", "fetched_at"])
    return snapshot
