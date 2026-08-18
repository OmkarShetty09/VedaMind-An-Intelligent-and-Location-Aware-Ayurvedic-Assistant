"""Append-only audit write for every guardrail decision (liability spine)."""

import logging

logger = logging.getLogger("apps.interactions_log")


def log_decision(request, herbs, drugs, ambiguous, result):
    try:
        from apps.interactions_log.models import GuardrailDecision

        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_anonymous", False):
            user = None
        GuardrailDecision.objects.create(
            user=user,
            conversation=getattr(request, "conversation", None),
            message=getattr(request, "message", None),
            entities={"herbs": herbs, "drugs": drugs, "ambiguous": ambiguous},
            matched_rules=[m.pair for m in result.matches],
            severity=max((m.severity for m in result.matches), default="none"),
            decision=result.overall,
            reason_code=result.reason_code,
            engine_version=result.engine_version,
        )
    except Exception:
        logger.exception("Failed to write guardrail audit row (audit must not break the request).")
