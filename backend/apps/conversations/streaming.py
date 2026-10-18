"""SSE encoding + server-side proxy of the RAG /chat stream.

Django acts as the gateway: it authenticates, persists, and forwards to the
internal RAG service, translating its stream events 1:1 to the client.
"""

import json
import logging

import httpx
from django.conf import settings
from django.http import StreamingHttpResponse

logger = logging.getLogger(__name__)

# Turns that are not an answer about Ayurveda: no "what not to take it with" panel.
_NO_CAUTIONS_REASONS = {"greeting", "empty_kb"}


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def turn_cautions(user_message: str, answer: str, medications: list[str]) -> dict:
    """Interaction cautions for the herbs in this turn; a lookup failure never breaks the answer."""
    from apps.guardrails.cautions import GENERAL_NOTE, cautions_for

    try:
        return cautions_for(f"{user_message}\n{answer}", medications)
    except Exception:
        logger.exception("Cautions lookup failed")
        return {"herbs": [], "items": [], "general": GENERAL_NOTE, "note": ""}


def stream_chat(user_id, user_message, context_bundle, session_id, correlation_id, user_message_id=None):
    """Returns a StreamingHttpResponse that proxies the RAG stream."""

    def event_stream():
        from .models import Conversation, Message

        conversation = Conversation.objects.get(pk=session_id)
        assistant = None

        payload = {
            "message": user_message,
            "session_id": str(session_id),
            "message_id": str(user_message_id) if user_message_id else None,
            "context": context_bundle,
        }
        try:
            with httpx.stream(
                "POST",
                f"{settings.RAG_SERVICE_URL}/api/v1/chat",
                json=payload,
                headers={"X-RAG-Admin-Token": settings.RAG_ADMIN_TOKEN, "X-Correlation-ID": correlation_id},
                timeout=httpx.Timeout(90.0, connect=10.0),
            ) as resp:
                if resp.status_code != 200:
                    yield sse(
                        "error",
                        {"code": "rag_unavailable", "message": f"RAG service returned {resp.status_code}"},
                    )
                    return
                content_parts = []
                citations = []
                model = ""
                tokens = 0
                blocked = False
                block_reason = ""
                rag_reason = ""
                guardrail_data = None
                low_confidence = False
                context_chip = None
                clarifying_question = None
                for line in resp.iter_lines():
                    if not line:
                        continue
                    if not line.startswith("data:"):
                        continue
                    try:
                        event = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue
                    etype = event.get("type")
                    if etype == "token":
                        content_parts.append(event["delta"])
                        yield sse("token", {"delta": event["delta"]})
                    elif etype == "guardrail":
                        guardrail_data = event
                        yield sse("guardrail", event)
                    elif etype == "citation":
                        citations = event.get("sources", [])
                        yield sse("citation", event)
                    elif etype == "context_chip":
                        context_chip = event.get("chip", "")
                        yield sse("context_chip", event)
                    elif etype == "low_confidence":
                        low_confidence = True
                        yield sse("low_confidence", event)
                    elif etype == "clarifying_question":
                        clarifying_question = event.get("question", "")
                        yield sse("clarifying_question", event)
                    elif etype == "done":
                        model = event.get("model", "")
                        tokens = event.get("tokens", 0)
                        # reason_code is also set on normal turns (greeting, empty_kb); only `blocked` means refused.
                        blocked = bool(event.get("blocked"))
                        rag_reason = event.get("reason_code", "") or ""
                        if blocked:
                            block_reason = event.get("reason_code", "") or (guardrail_data or {}).get("reason_code", "")
                        low_confidence = low_confidence or bool(event.get("low_confidence"))
                        break
                    elif etype == "error":
                        yield sse(
                            "error",
                            {"code": event.get("code", "rag_error"), "message": event.get("message", "")},
                        )
                        return

                answer = "".join(content_parts)
                cautions = {}
                if answer and not blocked and not clarifying_question and rag_reason not in _NO_CAUTIONS_REASONS:
                    cautions = turn_cautions(user_message, answer, context_bundle.get("medications") or [])
                assistant = Message.objects.create(
                    conversation=conversation,
                    role="assistant",
                    content=answer or clarifying_question or None,
                    source_citations=citations,
                    cautions=cautions,
                    llm_model=model,
                    tokens=tokens,
                    block_reason=block_reason[:48],
                )
                conversation.save(update_fields=["updated_at"])
                done_payload = {
                    "message_id": str(assistant.id),
                    "session_id": str(session_id),
                    "tokens": tokens,
                    "model": model,
                    "blocked": blocked,
                }
                if block_reason:
                    done_payload["reason_code"] = block_reason
                if low_confidence:
                    done_payload["low_confidence"] = True
                if guardrail_data:
                    done_payload["guardrail"] = guardrail_data
                if context_chip:
                    done_payload["context_chip"] = context_chip
                if clarifying_question:
                    done_payload["clarifying_question"] = clarifying_question
                if cautions:
                    done_payload["cautions"] = cautions
                yield sse("done", done_payload)
        except httpx.HTTPError as exc:
            logger.warning("RAG stream failed for %s: %s", correlation_id, exc)
            yield sse("error", {"code": "rag_unavailable", "message": "Could not reach the answer engine."})
        except Exception:
            logger.exception("Unexpected chat stream error")
            yield sse("error", {"code": "internal", "message": "An unexpected error occurred."})

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
