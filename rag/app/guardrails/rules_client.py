"""Client to the Django rules engine (the binding safety check).

Called BEFORE generation on every chat request. Any transport/parse failure
maps to fail-closed (NEEDS_REVIEW), never to PASS.
"""

import httpx

from app.config import get_settings

from .decision import GuardrailResult

_TIMEOUT = 15.0


def check(
    text: str,
    context: dict,
    conversation_id: str | None = None,
    message_id: str | None = None,
) -> GuardrailResult:
    settings = get_settings()
    payload = {
        "text": text[:4000],
        "context": {
            "conditions": context.get("conditions", []),
            "pregnancy": bool(context.get("pregnancy")),
            "pediatric": bool(context.get("pediatric")),
        },
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if message_id:
        payload["message_id"] = message_id
    try:
        resp = httpx.post(
            settings.backend_guardrail_url,
            json=payload,
            headers={"X-RAG-Admin-Token": settings.rag_admin_token},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return GuardrailResult(
            decision=data.get("decision", "needs_review"),
            severity=data.get("severity", "unknown"),
            reason_code=data.get("reason_code", "unknown"),
            matches=data.get("matches", []),
        )
    except (httpx.HTTPError, ValueError) as exc:
        # Fail closed: rules engine unreachable must never mean "safe".
        return GuardrailResult.fail_closed(f"guardrail service unreachable: {exc}")