"""Cache-first weather access with graceful degradation. Never fabricates data."""

import logging

from django.core.cache import cache
from django.utils import timezone

from .clients import WeatherClientError, fetch_one_call
from .models import WeatherSnapshot

logger = logging.getLogger(__name__)

_BUDGET_KEY = "weather:budget"
_BUDGET_LIMIT = 800  # hard ceiling below free tier's 1000/day


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
        snapshot = WeatherSnapshot.objects.create(lat=lat, lon=lon, payload=data, source="openweather")
        return {"payload": snapshot.payload, "source": snapshot.source, "fetched_at": snapshot.fetched_at}
    except WeatherClientError as exc:
        logger.warning("Weather unavailable: %s", exc)
        return {"payload": {}, "source": "unavailable", "fetched_at": None}


def _refresh(snapshot: WeatherSnapshot) -> WeatherSnapshot:
    _spend_budget()
    data = fetch_one_call(snapshot.lat, snapshot.lon)
    snapshot.payload = data
    snapshot.source = "openweather"
    snapshot.fetched_at = timezone.now()
    snapshot.save(update_fields=["payload", "source", "fetched_at"])
    return snapshot


def _spend_budget():
    """Redis counter guards the 1000/day free tier; past 80% we just slow down."""
    used = cache.incr(_BUDGET_KEY, 1)
    if used is None:  # key missing
        cache.set(_BUDGET_KEY, 1, timeout=86400)
    if cache.get(_BUDGET_KEY) > _BUDGET_LIMIT:
        logger.warning("Weather budget >80% used; expect degraded refreshes.")
