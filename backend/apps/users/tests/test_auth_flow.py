"""Auth flow against the real views: register, login, cookie refresh rotation, logout revocation."""

import pytest
from django.conf import settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

PASSWORD = "Sup3r-Secret-pass!"
COOKIE = settings.REFRESH_COOKIE_NAME


def register(client, email="Person@Example.com", **extra):
    return client.post("/api/v1/auth/register", {"email": email, "password": PASSWORD, **extra}, format="json")


def test_register_lowercases_email_so_login_finds_the_account():
    client = APIClient()
    response = register(client, name="")
    assert response.status_code == 201
    user = response.json()["user"]
    assert user["email"] == "person@example.com"
    assert user["name"] == "person"  # blank display name falls back to the email local part

    login = APIClient().post("/api/v1/auth/login", {"email": "PERSON@example.com", "password": PASSWORD}, format="json")
    assert login.status_code == 200
    assert login.json()["access"]


def test_register_rejects_duplicate_email_in_any_case():
    register(APIClient())
    response = register(APIClient(), email="person@EXAMPLE.com")
    assert response.status_code == 400
    assert "email" in response.json()["error"]["fields"]


def test_register_stores_a_valid_browser_timezone_and_ignores_unknown_ones():
    ok = register(APIClient(), email="a@example.com", timezone="Asia/Kolkata")
    assert ok.json()["user"]["timezone"] == "Asia/Kolkata"
    odd = register(APIClient(), email="b@example.com", timezone="Mars/Olympus")
    assert odd.status_code == 201
    assert odd.json()["user"]["timezone"] == "UTC"


def test_register_rejects_short_password_with_field_error():
    response = APIClient().post(
        "/api/v1/auth/register", {"email": "c@example.com", "password": "short"}, format="json"
    )
    assert response.status_code == 400
    assert "password" in response.json()["error"]["fields"]


def test_refresh_uses_cookie_and_rotates_it():
    client = APIClient()
    register(client)
    original = client.cookies[COOKIE].value

    response = client.post("/api/v1/auth/refresh", {}, format="json")
    assert response.status_code == 200
    body = response.json()
    assert body["access"]
    assert "refresh" not in body  # the refresh secret only travels in the httponly cookie
    rotated = client.cookies[COOKIE].value
    assert rotated and rotated != original

    me = APIClient()
    me.credentials(HTTP_AUTHORIZATION=f"Bearer {body['access']}")
    assert me.get("/api/v1/users/me").status_code == 200

    replay = APIClient()
    replay.cookies[COOKIE] = original
    assert replay.post("/api/v1/auth/refresh", {}, format="json").status_code == 401


def test_refresh_without_cookie_is_401():
    assert APIClient().post("/api/v1/auth/refresh", {}, format="json").status_code == 401


def test_logout_revokes_refresh_token_without_needing_access_token():
    client = APIClient()
    register(client)
    token = client.cookies[COOKIE].value

    assert client.post("/api/v1/auth/logout").status_code == 204

    reuse = APIClient()
    reuse.cookies[COOKIE] = token
    assert reuse.post("/api/v1/auth/refresh", {}, format="json").status_code == 401


def authed_client():
    client = APIClient()
    access = register(client).json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


def test_location_rejects_bad_input_with_400(monkeypatch):
    monkeypatch.setattr("apps.weather.clients.reverse_geocode", lambda lat, lon: "Bengaluru, Karnataka")
    client = authed_client()
    assert client.post("/api/v1/users/me/location", {"lat": "abc", "lon": "x"}, format="json").status_code == 400
    assert client.post("/api/v1/users/me/location", {"lat": 91, "lon": 0}, format="json").status_code == 400
    assert client.post("/api/v1/users/me/location", {"lon": 10}, format="json").status_code == 400

    ok = client.post("/api/v1/users/me/location", {"lat": 12.97, "lon": 77.59}, format="json")
    assert ok.status_code == 200
    assert ok.json()["place_name"] == "Bengaluru, Karnataka"


def test_location_place_name_refreshes_after_moving(monkeypatch):
    places = iter(["Bengaluru, Karnataka", "Mysuru, Karnataka"])
    monkeypatch.setattr("apps.weather.clients.reverse_geocode", lambda lat, lon: next(places))
    client = authed_client()
    client.post("/api/v1/users/me/location", {"lat": 12.97, "lon": 77.59}, format="json")
    moved = client.post("/api/v1/users/me/location", {"lat": 12.30, "lon": 76.64}, format="json")
    assert moved.json()["place_name"] == "Mysuru, Karnataka"


def test_health_details_replace_active_lists():
    client = authed_client()
    client.patch("/api/v1/users/me/medications", {"medications": ["warfarin 5 mg", "metformin"]}, format="json")
    client.patch("/api/v1/users/me/conditions", {"conditions": ["type 2 diabetes"]}, format="json")
    client.patch("/api/v1/users/me/medications", {"medications": ["levothyroxine", " "]}, format="json")

    me = client.get("/api/v1/users/me").json()
    assert [m["free_text"] for m in me["medications"]] == ["levothyroxine"]
    assert [c["condition"] for c in me["conditions"]] == ["type 2 diabetes"]
