"""Deterministic dosha scoring. Versioned: any change to the algorithm bumps QUIZ_VERSION."""

QUIZ_VERSION = "1.0"

_WEIGHTS = {"physical": 1.0, "mental": 1.0, "digestive": 1.5, "sleep": 1.2}


def score(answers: dict) -> dict:
    """answers: {question_key: {"dosha": "vata"|"pitta"|"kapha", "value": 0..3}}.

    Returns {vata, pitta, kapha, dominant_dosha} with normalized percentages.
    """
    totals = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
    weights = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
    for q, payload in (answers or {}).items():
        dosha = payload.get("dosha")
        value = int(payload.get("value", 0))
        category = _category_of(q)
        weight = _WEIGHTS.get(category, 1.0)
        if dosha in totals:
            totals[dosha] += value * weight
            weights[dosha] += weight

    scores = {d: round((totals[d] / weights[d] * 100) if weights[d] else 0.0, 1) for d in totals}
    dominant = max(scores, key=scores.get) if any(scores.values()) else ""
    return {"scores": scores, "dominant_dosha": dominant, "quiz_version": QUIZ_VERSION}


def _category_of(question_key: str) -> str:
    for cat in _WEIGHTS:
        if cat in question_key:
            return cat
    return "other"
