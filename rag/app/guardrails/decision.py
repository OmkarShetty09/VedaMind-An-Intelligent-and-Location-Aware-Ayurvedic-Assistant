"""Mapping of the Django rules-engine decision to pipeline behavior.

The Django engine is the BINDING safety layer (Section 4). This module only
decides what the RAG pipeline does with that verdict.
"""

PASS = "pass"
CAUTION = "caution"
BLOCK = "block"
NEEDS_REVIEW = "needs_review"

STOP_GENERATION = {BLOCK, NEEDS_REVIEW}
ALLOW_GENERATION = {PASS, CAUTION}


class GuardrailResult:
    def __init__(
        self,
        decision: str,
        severity: str,
        reason_code: str,
        matches: list,
        source: str = "rules_engine",
        entities: dict | None = None,
    ):
        self.decision = decision
        self.severity = severity
        self.reason_code = reason_code
        self.matches = matches
        self.source = source
        self.entities = entities or {}

    @classmethod
    def fail_closed(cls, message: str) -> "GuardrailResult":
        return cls(NEEDS_REVIEW, "unknown", "engine_error_fail_closed", [], source=message)

    @property
    def allows_generation(self) -> bool:
        return self.decision in ALLOW_GENERATION

    def to_event(self) -> dict:
        return {
            "decision": self.decision,
            "severity": self.severity,
            "reason_code": self.reason_code,
            "source": self.source,
            # What the user sees in the banner: the matched pair and the rule's guidance.
            "matches": [
                {"pair": m.get("pair", ""), "recommendation": m.get("recommendation", "")}
                for m in self.matches
                if isinstance(m, dict)
            ],
        }