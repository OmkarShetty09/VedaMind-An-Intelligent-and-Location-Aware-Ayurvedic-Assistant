"""Fail-closed on transport/parse failure: NEVER pass on error."""

import httpx

from app.guardrails import rules_client


def test_http_error_fails_closed(monkeypatch):
    def boom(*args, **kwargs):
        raise httpx.ConnectError("no backend")

    monkeypatch.setattr(rules_client.httpx, "post", boom)
    result = rules_client.check("ashwagandha", {}, None, None)
    assert result.decision == "needs_review"
    assert result.reason_code != "pass"


def test_bad_json_fails_closed(monkeypatch):
    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("bad json")

    monkeypatch.setattr(rules_client.httpx, "post", lambda *a, **k: Resp())
    result = rules_client.check("triphala", {}, None, None)
    assert result.decision == "needs_review"


def test_payload_built_with_context_flags(monkeypatch):
    captured = {}

    class Resp:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return self._payload

    def fake_post(url, json, headers, timeout):
        captured.update(json)
        return Resp({"decision": "caution", "severity": "low", "reason_code": "classical_only", "matches": []})

    monkeypatch.setattr(rules_client.httpx, "post", fake_post)
    result = rules_client.check("tulsi", {"pregnancy": True}, "c1", "m1")
    assert captured["context"]["pregnancy"] is True
    assert captured["conversation_id"] == "c1"
    assert captured["message_id"] == "m1"
    assert result.reason_code == "classical_only"