import httpx

_TIMEOUT = 5.0
_BASE = "https://api.open-meteo.com/v1/forecast"

_WMO_DESCRIPTIONS = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


class WeatherClientError(Exception):
    pass


def fetch_one_call(lat: float, lon: float) -> dict:
    """Fetch current weather from Open-Meteo. Raises WeatherClientError on any fault."""
    try:
        resp = httpx.get(
            _BASE,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": "auto",
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
    return _normalize(data)


def _normalize(data: dict) -> dict:
    """Convert Open-Meteo response to the shape downstream code expects.

    Open-Meteo:  current.temperature_2m, current.relative_humidity_2m, current.weather_code
    Expected:   current.temp, current.humidity, current.weather[0].description
    """
    raw = data["current"]
    code = raw.get("weather_code", 0)
    description = _WMO_DESCRIPTIONS.get(code, f"weather code {code}")

    return {
        "current": {
            "temp": raw.get("temperature_2m"),
            "humidity": raw.get("relative_humidity_2m"),
            "feels_like": raw.get("apparent_temperature"),
            "wind_speed": raw.get("wind_speed_10m"),
            "weather": [{"description": description}],
        },
    }
