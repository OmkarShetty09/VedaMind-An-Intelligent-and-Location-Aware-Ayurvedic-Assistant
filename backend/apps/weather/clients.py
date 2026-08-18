import httpx
from django.conf import settings

_TIMEOUT = 5.0
_BASE = "https://api.openweathermap.org/data/3.0/onecall"


class WeatherClientError(Exception):
    pass


def fetch_one_call(lat: float, lon: float) -> dict:
    """Fetch One Call 3.0 current weather. Raises WeatherClientError on any fault."""
    if not settings.OPENWEATHER_API_KEY:
        raise WeatherClientError("OPENWEATHER_API_KEY not configured")
    try:
        resp = httpx.get(
            _BASE,
            params={
                "lat": lat,
                "lon": lon,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric",
                "exclude": "minutely,hourly,daily,alerts",
            },
            timeout=_TIMEOUT,
        )
    except httpx.HTTPError as exc:
        raise WeatherClientError(f"transport error: {exc}") from exc
    if resp.status_code == 429:
        raise WeatherClientError("rate limited (429)")
    if resp.status_code != 200:
        raise WeatherClientError(f"http {resp.status_code}")
    try:
        data = resp.json()
    except ValueError as exc:
        raise WeatherClientError("malformed payload") from exc
    if "current" not in data:
        raise WeatherClientError("missing current block")
    return data
