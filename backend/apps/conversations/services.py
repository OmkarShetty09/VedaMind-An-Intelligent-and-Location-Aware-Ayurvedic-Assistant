"""Assembly of the user context bundle sent to the RAG service.

The bundle is attached server-side; the client never supplies it, so prompt
injection cannot alter guardrail context.
"""

from apps.weather.models import GeoLocation


def build_context_bundle(user, recent_messages) -> dict:
    profile = getattr(user, "dosha_profile", None)
    meds = list(user.medications.filter(active=True).values_list("free_text", flat=True))
    conditions = list(user.conditions.filter(active=True).values_list("condition", flat=True))
    geo = GeoLocation.objects.filter(user=user).first()

    weather = {}
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

    return {
        "dosha": {
            "dominant_dosha": (profile.dominant_dosha if profile else ""),
            "scores": (profile.vikriti_scores if profile else {}),
        },
        "medications": meds,
        "conditions": conditions,
        "pregnancy": any(c.lower() in ("pregnancy", "pregnant") for c in conditions),
        "pediatric": any("child" in c.lower() or "pediatric" in c.lower() for c in conditions),
        "location": (
            {"lat": geo.lat, "lon": geo.lon, "source": geo.source, "accuracy": geo.accuracy}
            if geo
            else None
        ),
        "weather": weather,
        "history": [{"role": m.role, "content": m.content} for m in recent_messages],
    }
