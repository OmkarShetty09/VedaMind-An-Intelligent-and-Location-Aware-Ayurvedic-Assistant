"""Greeting detection and conversational behavior tests."""

import json

from app.core.orchestrator import _is_greeting, _greeting_response, run


def collect(events):
    return [json.loads(e[len("data: ") :]) for e in events]


class TestIsGreeting:
    def test_hi(self):
        assert _is_greeting("hi")

    def test_hello(self):
        assert _is_greeting("hello")

    def test_hey(self):
        assert _is_greeting("hey")

    def test_namaste(self):
        assert _is_greeting("namaste")

    def test_namaskar(self):
        assert _is_greeting("namaskar")

    def test_good_morning(self):
        assert _is_greeting("good morning")

    def test_good_evening(self):
        assert _is_greeting("good evening")

    def test_whats_up(self):
        assert _is_greeting("what's up")

    def test_yo(self):
        assert _is_greeting("yo")

    def test_greetings(self):
        assert _is_greeting("greetings")

    def test_with_punctuation(self):
        assert _is_greeting("hi!")
        assert _is_greeting("hello?")
        assert _is_greeting("hey.")

    def test_with_whitespace(self):
        assert _is_greeting("  hi  ")
        assert _is_greeting("\thello\n")

    def test_case_insensitive(self):
        assert _is_greeting("HI")
        assert _is_greeting("Hello")
        assert _is_greeting("HEY")

    def test_not_greeting_substantive(self):
        assert not _is_greeting("hi, can you tell me about ashwagandha?")
        assert not _is_greeting("hello, I need help with digestion")
        assert not _is_greeting("hey what herbs help with sleep")

    def test_not_greeting_random(self):
        assert not _is_greeting("what is Ayurveda?")
        assert not _is_greeting("tell me about triphala")
        assert not _is_greeting("")

    def test_howdy(self):
        assert _is_greeting("howdy")


class TestGreetingResponse:
    def test_new_user_no_profile(self, monkeypatch):
        monkeypatch.setattr(
            "app.core.orchestrator.router.generate",
            lambda messages, tier: iter(["Hi! I'm VedaMind."]),
        )
        events = collect(list(_greeting_response("hello", {"has_dosha_profile": False})))
        tokens = "".join(e["delta"] for e in events if e["type"] == "token")
        done = next(e for e in events if e["type"] == "done")
        assert "VedaMind" in tokens
        assert done["reason_code"] == "greeting"
        assert done["blocked"] is False

    def test_existing_profile_references_dosha(self, monkeypatch):
        monkeypatch.setattr(
            "app.core.orchestrator.router.generate",
            lambda messages, tier: iter(["Good to see you again, Vata person."]),
        )
        context = {
            "has_dosha_profile": True,
            "dosha": {"dominant_dosha": "vata", "secondary_dosha": "pitta"},
        }
        events = collect(list(_greeting_response("hi", context)))
        tokens = "".join(e["delta"] for e in events if e["type"] == "token")
        done = next(e for e in events if e["type"] == "done")
        assert "vata" in tokens.lower() or "Vata" in tokens
        assert done["reason_code"] == "greeting"

    def test_llm_failure_fallback_new_user(self, monkeypatch):
        def fail(*a, **kw):
            raise RuntimeError("LLM unavailable")

        monkeypatch.setattr("app.core.orchestrator.router.generate", fail)
        events = collect(list(_greeting_response("hello", {"has_dosha_profile": False})))
        tokens = "".join(e["delta"] for e in events if e["type"] == "token")
        assert "VedaMind" in tokens
        assert "Ayurvedic constitution" in tokens or "Prakriti assessment" in tokens

    def test_llm_failure_fallback_existing_profile(self, monkeypatch):
        def fail(*a, **kw):
            raise RuntimeError("LLM unavailable")

        monkeypatch.setattr("app.core.orchestrator.router.generate", fail)
        context = {
            "has_dosha_profile": True,
            "dosha": {"dominant_dosha": "kapha", "secondary_dosha": ""},
        }
        events = collect(list(_greeting_response("hi", context)))
        tokens = "".join(e["delta"] for e in events if e["type"] == "token")
        assert "kapha" in tokens.lower() or "Kapha" in tokens

    def test_no_citations_for_greeting(self, monkeypatch):
        monkeypatch.setattr(
            "app.core.orchestrator.router.generate",
            lambda messages, tier: iter(["Hello!"]),
        )
        events = collect(list(_greeting_response("hello", {"has_dosha_profile": False})))
        citation = next(e for e in events if e["type"] == "citation")
        assert citation["sources"] == []


class TestOrchestratorGreetingIntegration:
    def test_greeting_skips_retrieval_and_rag(self, monkeypatch):
        from app.core import orchestrator

        retrieval_called = {"called": False}

        def fake_hybrid(*a, **kw):
            retrieval_called["called"] = True
            return []

        monkeypatch.setattr(orchestrator, "get_store", lambda: None)
        monkeypatch.setattr(orchestrator, "hybrid_search", fake_hybrid)
        monkeypatch.setattr(
            orchestrator.router, "generate", lambda messages, tier: iter(["Hey there!"])
        )

        events = collect(list(orchestrator.run("hi", {"has_dosha_profile": False})))
        done = next(e for e in events if e["type"] == "done")
        assert done["reason_code"] == "greeting"
        assert not retrieval_called["called"], "retrieval must not be called for greetings"

    def test_non_greeting_proceeds_normally(self, monkeypatch):
        from app.core import orchestrator
        from app.retrieval.stores.base import Passage

        monkeypatch.setattr(orchestrator, "get_store", lambda: type("S", (), {"count_chunks": lambda self: 100})())
        monkeypatch.setattr(orchestrator, "embed_query", lambda q: [0.5] * 8)
        monkeypatch.setattr(
            orchestrator,
            "hybrid_search",
            lambda e, q, f: [Passage(chunk_id="c1", text="passage", metadata={}, score=0.9)],
        )
        monkeypatch.setattr(orchestrator, "rerank", lambda ps, q: ps)
        monkeypatch.setattr(orchestrator, "_is_greeting", lambda q: False)

        events = collect(list(orchestrator.run("what is ashwagandha?", {})))
        done = next(e for e in events if e["type"] == "done")
        assert done["reason_code"] != "greeting"
