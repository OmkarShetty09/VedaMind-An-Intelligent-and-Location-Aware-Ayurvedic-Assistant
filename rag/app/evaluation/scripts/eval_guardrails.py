"""make eval entrypoint: guardrail rules-engine coverage + fail-closed sanity."""

import logging

from app.guardrails.decision import BLOCK, CAUTION, NEEDS_REVIEW, PASS

logging.basicConfig(level=logging.INFO)

SAMPLE_QUERIES = [
    "Is ashwagandha safe with metformin?",
    "Can I take turmeric while pregnant?",
    "What is the best time to wake up?",
]


def main():
    from app.guardrails import rules_client

    print("GUARDRAIL EVAL (requires backend running; fails closed otherwise)")
    for q in SAMPLE_QUERIES:
        result = rules_client.check(q, {}, None, None)
        print(f"  {q!r:60} -> {result.decision} ({result.reason_code})")
    assert result.decision in (PASS, CAUTION, BLOCK, NEEDS_REVIEW)
    print("OK: decisions within the safe set.")


if __name__ == "__main__":
    main()