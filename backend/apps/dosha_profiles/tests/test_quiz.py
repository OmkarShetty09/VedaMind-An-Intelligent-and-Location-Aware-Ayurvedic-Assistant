"""The quiz lives in the database (QuizQuestion / DoshaInfo, seeded by migration) and drives scoring."""

import pytest
from rest_framework.test import APIClient

from apps.dosha_profiles.models import QuizQuestion
from apps.users.models import User

pytestmark = pytest.mark.django_db


def authed():
    user = User.objects.create_user(email="quiz@example.com", name="Q", password="Sup3r-Secret-pass!")
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_quiz_endpoint_serves_seeded_questions_without_scoring_keys():
    data = authed().get("/api/v1/dosha/quiz").json()
    assert len(data["questions"]) == 11
    first = data["questions"][0]
    assert first["key"] == "body_frame" and len(first["options"]) == 3
    assert all(isinstance(o, str) for o in first["options"])  # which dosha an option scores stays server-side
    assert [d["dosha"] for d in data["doshas"]] == ["vata", "pitta", "kapha"]


def test_scoring_uses_the_option_doshas_from_the_database():
    client = authed()
    answers = {q.key: 0 for q in QuizQuestion.objects.all()}
    question = QuizQuestion.objects.get(key="body_frame")
    question.options[0]["dosha"] = "kapha"  # an admin re-maps one option
    question.save()
    results = client.post("/api/v1/dosha/assess", {"answers": answers}, format="json").json()["results"]
    assert results["scores"] == {"vata": 10, "pitta": 0, "kapha": 1}
    assert results["dominant_dosha"] == "vata"


def test_inactive_questions_are_hidden_and_not_required():
    client = authed()
    QuizQuestion.objects.filter(key="spending_habits").update(active=False)
    assert len(client.get("/api/v1/dosha/quiz").json()["questions"]) == 10
    answers = {q.key: 1 for q in QuizQuestion.objects.filter(active=True)}
    response = client.post("/api/v1/dosha/assess", {"answers": answers}, format="json")
    assert response.json()["results"]["dominant_dosha"] == "pitta"


def test_invalid_answers_are_rejected():
    client = authed()
    complete = {q.key: 0 for q in QuizQuestion.objects.all()}
    for answers in (
        {"body_frame": 0},  # incomplete
        {f"x{i}": 0 for i in range(11)},  # unknown questions
        {**complete, "body_frame": 7},  # option out of range
        {**complete, "body_frame": "0"},  # not an option number
    ):
        assert client.post("/api/v1/dosha/assess", {"answers": answers}, format="json").status_code == 400


def test_chat_suggestions_come_from_the_database():
    from apps.conversations.models import ChatSuggestion

    client = authed()
    assert len(client.get("/api/v1/chat/suggestions").json()["results"]) == 4
    ChatSuggestion.objects.create(text="What is abhyanga?", order=99)
    assert client.get("/api/v1/chat/suggestions").json()["results"][-1] == "What is abhyanga?"
