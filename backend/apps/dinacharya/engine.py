"""Dinacharya engine: deterministic rules produce a citable schedule.

The LLM never invents activities or times. The activities are RoutineTemplate rows (edited in the
admin); this engine resolves their times against the user's sunrise/sunset, season, weather and
assessed dosha (dominant + secondary), and emits the structured schedule. Without a dosha
assessment the routine is the general one, flagged as not personalized.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from .kala import approx_sunrise, classify
from .ritu import season_for


@dataclass
class RoutineContext:
    date: date
    season: str
    kala_name: str
    local_time: str
    temperature_c: float | None
    humidity: float | None
    dominant_dosha: str
    secondary_dosha: str = ""
    sunrise: time | None = None
    sunset: time | None = None
    approximate_location: bool = False


ENGINE_VERSION = "3.0.0"
DOSHAS = ("vata", "pitta", "kapha")
_TEMPLATES_PATH = Path(__file__).resolve().parent / "data" / "routine_templates.json"


@lru_cache(maxsize=1)
def dosha_focus() -> dict:
    """One-line daily focus per dosha (data/routine_templates.json)."""
    return json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8")).get("dosha_focus", {})


def dosha_personalization(user) -> dict:
    """What the routine is tuned to, from the user's latest dosha assessment."""
    profile = getattr(user, "dosha_profile", None)
    dominant = (getattr(profile, "dominant_dosha", "") or "") if profile else ""
    if dominant not in DOSHAS:
        return {"assessed": False, "dominant": "", "secondary": "", "classification": "", "percentages": {},
                "focus": "", "secondary_focus": ""}
    secondary = getattr(profile, "secondary_dosha", "") or ""
    secondary = secondary if secondary in DOSHAS and secondary != dominant else ""
    counts = {d: (getattr(profile, "vikriti_scores", None) or {}).get(d, 0) or 0 for d in DOSHAS}
    total = sum(counts.values())
    percentages = {d: round(c * 100 / total) for d, c in counts.items()} if total else {}

    classification = ""
    assessments = getattr(user, "dosha_assessments", None)
    latest = assessments.order_by("-created_at").first() if assessments is not None else None
    if latest is not None:
        classification = (latest.results or {}).get("classification", "")
    classification = classification or ("dual" if secondary else "single")

    return {"assessed": True, "dominant": dominant, "secondary": secondary, "classification": classification,
            "percentages": percentages, "focus": dosha_focus().get(dominant, ""),
            "secondary_focus": dosha_focus().get(secondary, "") if secondary else ""}


def load_templates() -> list[dict]:
    from .models import RoutineTemplate

    return [t.as_dict() for t in RoutineTemplate.objects.filter(active=True)]


def build_routine(
    user,
    *,
    local_now: datetime | None = None,
    weather_payload: dict | None = None,
    lat: float | None = None,
    lon: float | None = None,
    northern: bool = True,
    templates: list[dict] | None = None,
) -> dict:
    """Compute today's routine for a user. Pure logic + deterministic rules.

    `templates` defaults to the active RoutineTemplate rows (tests pass them explicitly).
    """
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

    personalization = dosha_personalization(user)

    ctx = RoutineContext(
        date=day,
        season=season_for(day, northern=northern),
        kala_name=classify(local_now, sunrise, sunset).name,
        local_time=local_now.strftime("%H:%M"),
        temperature_c=temp,
        humidity=humidity,
        dominant_dosha=personalization["dominant"],
        secondary_dosha=personalization["secondary"],
        sunrise=sunrise,
        sunset=sunset,
        approximate_location=lat is None,
    )

    templates = templates if templates is not None else load_templates()
    activities = [a for a in (_render(t, ctx) for t in templates) if a is not None]
    # Present the day as a timeline; the template `order` only breaks ties between equal start times.
    activities.sort(key=lambda a: (a["start"], a["order"]))
    for position, activity in enumerate(activities):
        activity["order"] = position

    return {
        "date": day.isoformat(),
        "season": ctx.season,
        "engine_version": ENGINE_VERSION,
        "approximate_location": ctx.approximate_location,
        "kala": {"name": ctx.kala_name, "local_time": ctx.local_time},
        "personalization": personalization,
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
                "personalization": routine.get("personalization", {}),
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
            personalized=item.get("personalized", False),
            order=item["order"],
        )
    return rec


def _approx_sunset(day, lat, lon, offset_hours) -> "time":
    sr = approx_sunrise(day, lat, lon, offset_hours)

    hours = 12.07  # mean day length; fine for wellness windows
    total = sr.hour + sr.minute / 60 + hours
    total = total % 24
    return time(int(total), int(round((total - int(total)) * 60)) % 60)


def _render(template: dict, ctx: RoutineContext) -> dict | None:
    """One template -> one activity for this user/day, or None when its condition does not apply."""
    threshold = template.get("above_temperature_c")
    if threshold is not None and (ctx.temperature_c is None or ctx.temperature_c <= threshold):
        return None
    user_doshas = [d for d in (ctx.dominant_dosha, ctx.secondary_dosha) if d]
    only_for = template.get("doshas") or []
    if only_for and not set(only_for) & set(user_doshas):
        return None
    dosha_override = (template.get("dosha_overrides") or {}).get(ctx.dominant_dosha, {})
    merged = {
        **template,
        **(template.get("season_overrides") or {}).get(ctx.season, {}),
        **dosha_override,
    }

    def fill(text: str) -> str:
        return (text or "").replace("{dosha}", ctx.dominant_dosha).replace("{secondary}", ctx.secondary_dosha)

    tips = template.get("dosha_tips") or {}
    tip_reasons = []
    if tips.get(ctx.dominant_dosha):
        tip_reasons.append(f"For your {ctx.dominant_dosha.title()}: {tips[ctx.dominant_dosha]}")
    if ctx.secondary_dosha and tips.get(ctx.secondary_dosha):
        tip_reasons.append(f"For your secondary {ctx.secondary_dosha.title()}: {tips[ctx.secondary_dosha]}")

    return {
        "time_of_day": merged["time_of_day"],
        "start": _resolve_time(merged["start"], ctx),
        "end": _resolve_time(merged["end"], ctx) if merged.get("end") else None,
        "title": fill(merged["title"]),
        "description": fill(merged.get("description", "")),
        "reasons": [fill(r) for r in merged.get("reasons") or []] + tip_reasons,
        "citations": merged.get("citations") or [],
        "dosha_target": fill(merged.get("dosha_target", "")),
        "order": merged.get("order", 0),
        "personalized": bool(only_for or dosha_override or tip_reasons),
    }


def _parse_clock(value: str) -> time:
    hours, minutes = value.split(":")
    return time(int(hours), int(minutes))


def _resolve_time(spec: dict, ctx: RoutineContext) -> time:
    """{"anchor": "sunrise"|"sunset"|"clock", "offset_minutes", "clock", "fallback_clock"} -> local time."""
    anchor = spec.get("anchor", "clock")
    if anchor == "clock":
        return _parse_clock(spec["clock"])
    base = ctx.sunrise if anchor == "sunrise" else ctx.sunset
    if base is None:
        base = _parse_clock(spec["fallback_clock"])
    moment = datetime.combine(ctx.date, base) + timedelta(minutes=int(spec.get("offset_minutes", 0)))
    return moment.time()
