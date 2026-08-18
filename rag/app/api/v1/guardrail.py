from fastapi import APIRouter
from pydantic import BaseModel

from app.guardrails import secondary_check
from app.guardrails.decision import GuardrailResult

router = APIRouter()


class SecondaryRequest(BaseModel):
    pair: str
    context: dict = {}


@router.post("/guardrail/secondary")
def secondary_review(payload: SecondaryRequest):
    """Expose the LLM secondary review for testing/audit. Never binding."""
    base = GuardrailResult("pass", "unknown", "no_rule_found", [])
    result = secondary_check.secondary_review(base, payload.pair, payload.context)
    return {"decision": result.decision, "reason_code": result.reason_code,
            "severity": result.severity, "source": result.source}