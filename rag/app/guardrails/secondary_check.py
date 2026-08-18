"""Optional LLM cross-check on novel combinations.

Can only ESCALATE (add a caution) — never downgrade a rules-engine verdict.
The rules engine remains the binding decision; this exists to avoid silent
passes on pairs the deterministic set doesn't cover.
"""

import json
import logging

from app.config import get_settings
from app.llm import router
from app.prompts import load_template

from .decision import GuardrailResult

logger = logging.getLogger("rag.guardrails.secondary")


def secondary_review(result: GuardrailResult, pair_text: str, context: dict) -> GuardrailResult:
    settings = get_settings()
    if not settings.openai_api_key and not settings.gemini_api_key:
        # No LLM configured: keep the engine verdict, but never let "no rule"
        # become a silent pass - engine already returns needs_review for those.
        return result
    if result.reason_code == "engine_error_fail_closed":
        return result

    template = load_template("guardrail_secondary.j2")
    messages = [
        {"role": "system", "content": "You are a conservative safety reviewer. You never claim anything is safe."},
        {"role": "user", "content": template.render(pair=pair_text[:500], context=json.dumps(context, ensure_ascii=False)[:800])},
    ]
    try:
        raw = router.complete(messages, tier="cheap", json_mode=True)
        parsed = json.loads(raw)
        severity = parsed.get("severity", "unknown")
        if severity in ("high", "moderate") and result.decision in ("pass", "caution"):
            # Escalate a PASS/CAUTION from the engine to NEEDS_REVIEW.
            return GuardrailResult(
                decision="needs_review",
                severity=severity,
                reason_code="secondary_escalation",
                matches=[{"pair": pair_text, "recommendation": parsed.get("recommendation", "")}],
                source="llm_secondary",
            )
    except Exception as exc:  # noqa: BLE001 - secondary review never breaks the request
        logger.warning("Secondary review failed (%s); keeping engine verdict.", exc)
    return result