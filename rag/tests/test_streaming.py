import json

from app.llm import streaming


def test_events_use_data_prefix():
    line = streaming.token_event("hello")
    assert line.startswith("data: ")


def test_guardrail_event_payload():
    line = streaming.guardrail_event({"decision": "caution", "reason_code": "classical_only"})
    data = json.loads(line[len("data: ") :])
    assert data["type"] == "guardrail"
    assert data["decision"] == "caution"


def test_done_event():
    line = streaming.done_event(blocked=True, reason_code="low_relevance", tokens=0, model="")
    data = json.loads(line[len("data: ") :])
    assert data["type"] == "done"
    assert data["blocked"] is True