from enum import IntEnum


class Decision(IntEnum):
    """Safety decision lattice. Monotonic: errors escalate, never downgrade.

    PASS < CAUTION < NEEDS_REVIEW < BLOCK
    """

    PASS = 0
    CAUTION = 1
    NEEDS_REVIEW = 2
    BLOCK = 3

    @property
    def label(self):
        labels = {self.PASS: "pass", self.CAUTION: "caution", self.NEEDS_REVIEW: "needs_review", self.BLOCK: "block"}
        return labels[self]


class ReasonCode:
    NO_RULE = "no_rule_found"
    INTERACTION_LOW = "interaction_low_severity"
    INTERACTION_MODERATE = "interaction_moderate"
    INTERACTION_HIGH = "interaction_high_or_severe"
    CLASSICAL_CAUTION = "classical_caution"
    ENTITY_AMBIGUOUS = "entity_ambiguous"
    NOVEL_PAIR = "novel_pair_unverified"
    POLYPHARMACY = "polypharmacy_compounded"
    CONTEXT_RULE = "context_specific_rule"
    ENGINE_ERROR = "engine_error_fail_closed"
    DOSE_BELOW_THRESHOLD = "dose_below_threshold"
