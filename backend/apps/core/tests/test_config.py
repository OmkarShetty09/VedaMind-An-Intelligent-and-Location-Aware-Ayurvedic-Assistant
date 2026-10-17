"""No hardcoded accounts or secrets: everything comes from settings/.env."""

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.users.models import User
from config.settings._checks import require_strong_secrets


@pytest.mark.django_db
def test_seed_creates_no_accounts_unless_configured(settings):
    settings.DEMO_USER_EMAIL = ""
    settings.DEMO_USER_PASSWORD = ""
    settings.ADMIN_EMAIL = ""
    settings.ADMIN_PASSWORD = ""
    call_command("seed_demo_data")
    call_command("create_superuser")
    assert not User.objects.exists()


@pytest.mark.django_db
def test_accounts_use_credentials_from_settings(settings):
    settings.DEMO_USER_EMAIL = "Viva@Example.com"
    settings.DEMO_USER_PASSWORD = "a-configured-password-123"
    settings.ADMIN_EMAIL = "boss@example.com"
    settings.ADMIN_PASSWORD = "another-configured-password-456"
    call_command("seed_demo_data")
    call_command("create_superuser")
    demo = User.objects.get(email="viva@example.com")
    assert demo.check_password("a-configured-password-123") and demo.consent_accepted
    assert User.objects.get(email="boss@example.com").is_superuser


@pytest.mark.parametrize("weak", ["change-me", "dev-token", "short"])
def test_production_refuses_weak_secrets(weak):
    with pytest.raises(ImproperlyConfigured):
        require_strong_secrets(DJANGO_SECRET_KEY=weak)
    require_strong_secrets(DJANGO_SECRET_KEY="x" * 40)


@pytest.mark.django_db
def test_city_search_endpoint(monkeypatch):
    place = {"name": "Mysuru", "region": "Karnataka, India", "label": "Mysuru, Karnataka", "lat": 12.3, "lon": 76.6}
    monkeypatch.setattr("apps.weather.views.search_places", lambda query: [place] if query == "Mysuru" else [])
    user = User.objects.create_user(email="c@example.com", name="C", password="Sup3r-Secret-pass!")
    client = APIClient()
    client.force_authenticate(user)
    assert client.get("/api/v1/weather/places?q=Mysuru").json()["results"] == [place]
    assert client.get("/api/v1/weather/places?q=M").json()["results"] == []  # too short to search

    saved = client.post(
        "/api/v1/users/me/location",
        {"lat": 12.3, "lon": 76.6, "source": "user", "place_name": "Mysuru, Karnataka"},
        format="json",
    ).json()
    assert saved["place_name"] == "Mysuru, Karnataka" and saved["source"] == "user"
