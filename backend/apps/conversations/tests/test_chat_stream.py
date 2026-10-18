"""ChatView -> RAG stream proxy, with the RAG service faked at the httpx boundary."""

import json

import pytest
from rest_framework.test import APIClient

from apps.conversations.models import Conversation, Message
from apps.users.models import User

pytestmark = pytest.mark.django_db


class FakeRagResponse:
    status_code = 200

    def __init__(self, events):
        self._lines = [f"data: {json.dumps(e)}" for e in events]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def iter_lines(self):
        yield from self._lines


def fake_rag(monkeypatch, events, captured=None):
    def stream(method, url, json=None, headers=None, timeout=None):
        if captured is not None:
            captured.update(json)
        return FakeRagResponse(events)

    monkeypatch.setattr("apps.conversations.streaming.httpx.stream", stream)


def consented_client():
    user = User.objects.create_user(email="chat@example.com", name="Chat", password="Sup3r-Secret-pass!")
    user.consent_accepted = True
    user.save(update_fields=["consent_accepted"])
    client = APIClient()
    client.force_authenticate(user)
    return client, user


def sse_events(response):
    body = b"".join(response.streaming_content).decode()
    events = []
    for frame in body.strip().split("\n\n"):
        name = next(line[6:].strip() for line in frame.splitlines() if line.startswith("event:"))
        data = json.loads(next(line[5:] for line in frame.splitlines() if line.startswith("data:")))
        events.append((name, data))
    return events


def test_greeting_with_reason_code_is_not_marked_blocked(monkeypatch):
    fake_rag(
        monkeypatch,
        [
            {"type": "token", "delta": "Hello!"},
            {"type": "citation", "sources": []},
            {"type": "done", "blocked": False, "reason_code": "greeting", "tokens": 0, "model": "cheap"},
        ],
    )
    client, _ = consented_client()
    events = sse_events(client.post("/api/v1/chat/", {"message": "hi"}, format="json"))
    done = dict(events)["done"]
    assert done["blocked"] is False
    assert "reason_code" not in done
    assistant = Message.objects.get(role="assistant")
    assert assistant.content == "Hello!"
    assert assistant.block_reason == ""


def test_blocked_turn_carries_reason_and_guardrail(monkeypatch):
    guardrail = {"type": "guardrail", "decision": "block", "reason_code": "interaction_high_or_severe",
                 "matches": [{"pair": "turmeric <-> warfarin", "recommendation": "Do not combine."}]}
    fake_rag(monkeypatch, [guardrail, {"type": "done", "blocked": True, "reason_code": "interaction_high_or_severe"}])
    client, _ = consented_client()
    events = sse_events(client.post("/api/v1/chat/", {"message": "turmeric with warfarin?"}, format="json"))
    done = dict(events)["done"]
    assert done["blocked"] is True
    assert done["reason_code"] == "interaction_high_or_severe"
    assert done["guardrail"]["matches"][0]["pair"] == "turmeric <-> warfarin"
    assert Message.objects.get(role="assistant").block_reason == "interaction_high_or_severe"


def test_clarifying_question_is_saved_as_assistant_text(monkeypatch):
    question = "Are you currently on any medication?"
    fake_rag(
        monkeypatch,
        [{"type": "clarifying_question", "question": question}, {"type": "done", "blocked": False}],
    )
    client, _ = consented_client()
    events = sse_events(client.post("/api/v1/chat/", {"message": "suggest a herb"}, format="json"))
    assert dict(events)["done"]["clarifying_question"] == question
    assert Message.objects.get(role="assistant").content == question


def test_context_bundle_sent_to_rag_has_profile_meds_and_ritu_season(monkeypatch):
    captured = {}
    fake_rag(monkeypatch, [{"type": "done", "blocked": False}], captured)
    client, user = consented_client()
    user.medications.create(free_text="warfarin 5 mg")
    sse_events(client.post("/api/v1/chat/", {"message": "hello there friend"}, format="json"))
    context = captured["context"]
    assert context["medications"] == ["warfarin 5 mg"]
    assert context["season"].split(" ")[0] in {"Vasant", "Grishma", "Varsha", "Sharad", "Hemant", "Shishir"}
    assert context["history"][-1] == {"role": "user", "content": "hello there friend"}


def test_new_conversation_gets_a_title_and_deleted_ones_are_hidden(monkeypatch):
    fake_rag(monkeypatch, [{"type": "done", "blocked": False}])
    client, _ = consented_client()
    events = sse_events(client.post("/api/v1/chat/", {"message": "What   is\nDinacharya?"}, format="json"))
    session_id = dict(events)["done"]["session_id"]
    assert Conversation.objects.get(pk=session_id).title == "What is Dinacharya?"

    assert client.delete(f"/api/v1/chat/sessions/{session_id}").status_code == 204
    assert client.get(f"/api/v1/chat/sessions/{session_id}").status_code == 404
    again = client.post("/api/v1/chat/", {"message": "more", "session_id": session_id}, format="json")
    assert again.status_code == 404


def test_chat_requires_consent():
    user = User.objects.create_user(email="noconsent@example.com", name="N", password="Sup3r-Secret-pass!")
    client = APIClient()
    client.force_authenticate(user)
    assert client.post("/api/v1/chat/", {"message": "hi"}, format="json").status_code == 403


def test_answers_carry_what_not_to_take_it_with(monkeypatch):
    from django.core.management import call_command

    call_command("seed_demo_data")
    fake_rag(
        monkeypatch,
        [
            {"type": "token", "delta": "Turmeric is warming and supports digestion [S1]."},
            {"type": "citation", "sources": [{"id": "S1", "source": "ayurwiki_herbs"}]},
            {"type": "done", "blocked": False, "tokens": 9, "model": "m"},
        ],
    )
    client, _ = consented_client()
    events = sse_events(client.post("/api/v1/chat/", {"message": "is it good for digestion?"}, format="json"))
    cautions = dict(events)["done"]["cautions"]
    assert cautions["herbs"] == ["turmeric"]
    assert "Warfarin" in {i["avoid_with"] for i in cautions["items"]}
    assert cautions["general"]
    assert Message.objects.get(role="assistant").cautions == cautions


def test_greetings_have_no_cautions(monkeypatch):
    fake_rag(monkeypatch, [{"type": "token", "delta": "Hello!"},
                           {"type": "done", "blocked": False, "reason_code": "greeting"}])
    client, _ = consented_client()
    events = sse_events(client.post("/api/v1/chat/", {"message": "hi"}, format="json"))
    assert "cautions" not in dict(events)["done"]
    assert Message.objects.get(role="assistant").cautions == {}
