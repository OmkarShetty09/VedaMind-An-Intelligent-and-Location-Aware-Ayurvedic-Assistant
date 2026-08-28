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


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


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
                block_reason = ""
                guardrail_data = None
                low_confidence = False
                context_chip = None
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
                        block_reason = event.get("decision", "")
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
                        yield sse("clarifying_question", event)
                    elif etype == "done":
                        model = event.get("model", "")
                        tokens = event.get("tokens", 0)
                        block_reason = event.get("reason_code", block_reason)
                        break
                    elif etype == "error":
                        yield sse(
                            "error",
                            {"code": event.get("code", "rag_error"), "message": event.get("message", "")},
                        )
                        return

                assistant = Message.objects.create(
                    conversation=conversation,
                    role="assistant",
                    content="".join(content_parts) or None,
                    source_citations=citations,
                    llm_model=model,
                    tokens=tokens,
                    block_reason=block_reason,
                )
                done_payload = {
                    "message_id": str(assistant.id),
                    "session_id": str(session_id),
                    "tokens": tokens,
                    "model": model,
                }
                if block_reason:
                    done_payload["blocked"] = True
                    done_payload["reason_code"] = block_reason
                if low_confidence:
                    done_payload["low_confidence"] = True
                if guardrail_data:
                    done_payload["guardrail"] = guardrail_data
                if context_chip:
                    done_payload["context_chip"] = context_chip
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
