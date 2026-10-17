"""Assembly of the user context bundle sent to the RAG service.

The bundle is attached server-side; the client never supplies it, so prompt
injection cannot alter guardrail context.
"""

from apps.weather.models import GeoLocation


def build_context_bundle(user, recent_messages, client_location=None):
    profile = getattr(user, "dosha_profile", None)
    meds = list(user.medications.filter(active=True).values_list("free_text", flat=True))
    conditions = list(user.conditions.filter(active=True).values_list("condition", flat=True))
    geo = GeoLocation.objects.filter(user=user).first()

    weather = {}
    location_data = None

    if geo is not None:
        from apps.weather.cache import get_weather

        result = get_weather(geo.lat, geo.lon)
        current = (result["payload"] or {}).get("current") or {}
        weather = {
            "temp_c": current.get("temp"),
            "humidity": current.get("humidity"),
            "condition": ((current.get("weather") or [{}])[0]).get("description", ""),
            "source": result["source"],
        }
        location_data = {"lat": geo.lat, "lon": geo.lon, "source": geo.source, "accuracy": geo.accuracy}

    if client_location:
        if not location_data and client_location.get("lat") and client_location.get("lon"):
            location_data = {"lat": client_location["lat"], "lon": client_location["lon"], "source": "client"}
        if client_location.get("current_weather"):
            cw = client_location["current_weather"]
            weather = {
                "temp_c": cw.get("temp_c", weather.get("temp_c")),
                "humidity": cw.get("humidity", weather.get("humidity")),
                "condition": cw.get("condition", weather.get("condition")),
                "source": weather.get("source", "client"),
            }
        if client_location.get("season"):
            weather["season"] = client_location["season"]

    lat = (location_data or {}).get("lat")
    season = _infer_season(weather, northern=lat is None or lat >= 0)

    return {
        "dosha": {
            "dominant_dosha": (profile.dominant_dosha if profile else ""),
            "secondary_dosha": (profile.secondary_dosha if profile else ""),
            "scores": (profile.vikriti_scores if profile else {}),
        },
        "has_dosha_profile": profile is not None,
        "medications": meds,
        "conditions": conditions,
        "pregnancy": any(c.lower() in ("pregnancy", "pregnant") for c in conditions),
        "pediatric": any("child" in c.lower() or "pediatric" in c.lower() for c in conditions),
        "location": location_data,
        "weather": weather,
        "season": season,
        "history": [{"role": m.role, "content": m.content} for m in recent_messages],
    }


def _infer_season(weather, northern=True):
    """Classical ritu, from the same calendar the Dinacharya engine uses so chat and routine agree."""
    season = weather.get("season")
    if season:
        return season
    import datetime

    from apps.dinacharya.ritu import season_for, season_info

    info = season_info(season_for(datetime.date.today(), northern=northern))
    return f"{info['key'].title()} ({info['english']})"
