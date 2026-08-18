"""Dinacharya engine: deterministic rules produce a citable schedule.

The LLM never invents activities or times. This engine emits the structured
schedule; the RAG service may only *render* it as prose.
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from .kala import approx_sunrise, classify
from .ritu import season_for
from .rules import evening, mealtime, morning, sleep


@dataclass
class RoutineContext:
    date: date
    season: str
    kala_name: str
    local_time: str
    temperature_c: float | None
    humidity: float | None
    dominant_dosha: str
    sunrise: time | None = None
    sunset: time | None = None
    approximate_location: bool = False


ENGINE_VERSION = "1.0.0"

_RULE_MODULES = (morning, mealtime, evening, sleep)


def build_routine(
    user,
    *,
    local_now: datetime | None = None,
    weather_payload: dict | None = None,
    lat: float | None = None,
    lon: float | None = None,
    northern: bool = True,
) -> dict:
    """Compute today's routine for a user. Pure logic + deterministic rules."""
    tz = ZoneInfo(user.timezone)
    local_now = local_now or datetime.now(tz)
    day = local_now.date()

    sunrise = sunset = None
    if lat is not None and lon is not None:
        offset = local_now.utcoffset().total_seconds() / 3600 if local_now.utcoffset() else 0.0
        sunrise = approx_sunrise(day, lat, lon, offset)
        sunset = _approx_sunset(day, lat, lon, offset)

    current = (weather_payload or {}).get("current") or {}
    temp = current.get("temp")
    humidity = current.get("humidity")

    profile = getattr(user, "dosha_profile", None)
    dominant = (profile.dominant_dosha if profile else "") or ""

    ctx = RoutineContext(
        date=day,
        season=season_for(day, northern=northern),
        kala_name=classify(local_now, sunrise, sunset).name,
        local_time=local_now.strftime("%H:%M"),
        temperature_c=temp,
        humidity=humidity,
        dominant_dosha=dominant or "vata",
        sunrise=sunrise,
        sunset=sunset,
        approximate_location=lat is None,
    )

    activities = []
    for module in _RULE_MODULES:
        activities.extend(module.build_activities(ctx))
    activities.sort(key=lambda a: a["order"])

    return {
        "date": day.isoformat(),
        "season": ctx.season,
        "engine_version": ENGINE_VERSION,
        "approximate_location": ctx.approximate_location,
        "kala": {"name": ctx.kala_name, "local_time": ctx.local_time},
        "activities": activities,
    }


def persist_routine(user, routine: dict) -> None:
    from .models import DinacharyaRecommendation, RoutineActivity

    day = date.fromisoformat(routine["date"])
    rec, created = DinacharyaRecommendation.objects.update_or_create(
        user=user,
        date=day,
        defaults={
            "season": routine["season"],
            "engine_version": routine["engine_version"],
            "inputs_snapshot": {
                "kala": routine["kala"],
                "approximate_location": routine["approximate_location"],
            },
        },
    )
    if not created:
        rec.activities.all().delete()
    for item in routine["activities"]:
        RoutineActivity.objects.create(
            recommendation=rec,
            time_of_day=item["time_of_day"],
            start=item["start"],
            end=item.get("end"),
            title=item["title"],
            description=item.get("description", ""),
            reasons=item.get("reasons", []),
            citations=item.get("citations", []),
            dosha_target=item.get("dosha_target", ""),
            order=item["order"],
        )
    return rec


def _approx_sunset(day, lat, lon, offset_hours) -> "time":
    sr = approx_sunrise(day, lat, lon, offset_hours)

    hours = 12.07  # mean day length; fine for wellness windows
    total = sr.hour + sr.minute / 60 + hours
    total = total % 24
    return time(int(total), int(round((total - int(total)) * 60)) % 60)
