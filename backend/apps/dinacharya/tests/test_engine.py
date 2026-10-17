import json
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from rest_framework.test import APIClient

from apps.dinacharya.engine import build_routine
from apps.dinacharya.ritu import season_for
from apps.users.models import User

# The shipped templates, without a database (the DB copy is seeded from this same file).
TEMPLATES = json.loads(
    (Path(__file__).resolve().parents[1] / "data" / "routine_templates.json").read_text(encoding="utf-8")
)["templates"]
IST = ZoneInfo("Asia/Kolkata")


class FakeProfile:
    def __init__(self, dosha):
        self.dominant_dosha = dosha


class FakeUser:
    timezone = "Asia/Kolkata"

    def __init__(self, dosha=None):
        self.dosha_profile = FakeProfile(dosha) if dosha else None


def routine_for(user=None, when=datetime(2026, 10, 17, 9, 0, tzinfo=IST), **kwargs):
    return build_routine(user or FakeUser(), local_now=when, templates=TEMPLATES, **kwargs)


def by_title(routine):
    return {a["title"]: a for a in routine["activities"]}


def test_routine_is_chronological_and_local_to_the_user():
    routine = routine_for(lat=12.97, lon=77.59, weather_payload={})
    starts = [a["start"] for a in routine["activities"]]
    assert starts == sorted(starts)
    assert [a["order"] for a in routine["activities"]] == list(range(len(starts)))
    wake = by_title(routine)["Warm water + tongue cleaning"]
    assert 5 <= wake["start"].hour <= 6  # Bengaluru sunrise ~06:10 local, wake 30 min before
    assert routine["season"] == "sharad"


def test_hot_weather_adds_afternoon_rest():
    may = datetime(2026, 5, 1, 9, 0, tzinfo=IST)
    assert "Afternoon rest" in by_title(routine_for(when=may, weather_payload={"current": {"temp": 39}}))
    assert "Afternoon rest" not in by_title(routine_for(when=may, weather_payload={"current": {"temp": 30}}))


def test_season_and_dosha_overrides():
    winter = by_title(routine_for(when=datetime(2026, 12, 5, 9, 0, tzinfo=IST)))
    assert "Self-massage (sesame oil)" in winter
    monsoon = by_title(routine_for(when=datetime(2026, 8, 5, 9, 0, tzinfo=IST)))
    assert "Self-massage (coconut oil)" in monsoon
    assert monsoon["Light dinner"]["description"].startswith("In the monsoon")

    kapha = by_title(routine_for(FakeUser("kapha")))["Sleep"]
    pitta = by_title(routine_for(FakeUser("pitta")))["Sleep"]
    assert (kapha["start"], pitta["start"]) == (time(21, 30), time(22, 30))
    assert "kapha constitution" in kapha["description"] and kapha["dosha_target"] == "kapha"


def test_no_location_uses_fallback_sun_times():
    routine = routine_for()
    assert routine["approximate_location"] is True
    assert by_title(routine)["Warm water + tongue cleaning"]["start"] == time(5, 30)
    assert by_title(routine)["Sunset walk"]["start"] == time(18, 30)


@pytest.mark.parametrize(
    ("day", "ritu"),
    [((1, 20), "hemant"), ((1, 21), "shishir"), ((3, 21), "vasant"), ((7, 21), "varsha"), ((11, 21), "hemant")],
)
def test_ritu_boundaries(day, ritu):
    assert season_for(date(2026, *day)) == ritu


@pytest.mark.django_db
def test_db_templates_are_seeded_and_admin_toggles_apply():
    from apps.dinacharya.engine import load_templates
    from apps.dinacharya.models import RoutineTemplate

    assert {t["key"] for t in load_templates()} == {t["key"] for t in TEMPLATES}
    RoutineTemplate.objects.filter(key="movement").update(active=False)
    assert "movement" not in {t["key"] for t in load_templates()}


@pytest.mark.django_db
def test_season_endpoint_is_public_and_hemisphere_aware():
    client = APIClient()
    north = client.get("/api/v1/dinacharya/season").json()
    south = client.get("/api/v1/dinacharya/season?lat=-33.9").json()
    assert {"key", "label", "english", "emoji"} <= set(north)
    assert north["key"] != south["key"]


@pytest.mark.django_db
def test_today_uses_the_users_local_date():
    user = User.objects.create_user(
        email="d@example.com", name="D", password="Sup3r-Secret-pass!", timezone="Pacific/Kiritimati"
    )
    client = APIClient()
    client.force_authenticate(user)
    generated = client.get("/api/v1/dinacharya/recommend")
    assert generated.status_code == 200
    assert generated.json()["season_info"]["label"]
    # UTC+14: the local date is usually "tomorrow" relative to the server's UTC date; /today must still find it.
    today = client.get("/api/v1/dinacharya/today")
    assert today.status_code == 200
    assert today.json()["date"] == generated.json()["date"]
