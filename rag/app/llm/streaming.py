"""Wire-format helpers for the RAG -> Django stream.

Each line is a JSON object on the standard `data:` prefix so Django can
forward it as an SSE event:  data: {"type": "token", "delta": "..."}
"""

import json


def emit(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def token_event(delta: str) -> str:
    return emit({"type": "token", "delta": delta})


def guardrail_event(payload: dict) -> str:
    return emit({"type": "guardrail", **payload})


def citation_event(sources: list[dict]) -> str:
    return emit({"type": "citation", "sources": sources})


def context_chip_event(chip: str) -> str:
    return emit({"type": "context_chip", "chip": chip})


def low_confidence_event() -> str:
    return emit({"type": "low_confidence"})


def clarifying_question_event(question: str) -> str:
    return emit({"type": "clarifying_question", "question": question})


def done_event(**kwargs) -> str:
    return emit({"type": "done", **kwargs})


def error_event(code: str, message: str) -> str:
    return emit({"type": "error", "code": code, "message": message})
