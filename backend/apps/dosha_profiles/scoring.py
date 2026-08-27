"""Deterministic dosha scoring. Versioned: any change to the algorithm bumps QUIZ_VERSION."""

QUIZ_VERSION = "2.0"

TOTAL_QUESTIONS = 11


def score(answers: dict) -> dict:
    """answers: {question_key: {"dosha": "vata"|"pitta"|"kapha", "value": 1}}.

    Simple A/B/C counting: A=Vata, B=Pitta, C=Kapha.
    Returns {scores, percentages, dominant_dosha, secondary_dosha, classification, quiz_version}.
    """
    counts = {"vata": 0, "pitta": 0, "kapha": 0}
    for q, payload in (answers or {}).items():
        dosha = payload.get("dosha")
        if dosha in counts:
            counts[dosha] += 1

    total = sum(counts.values()) or 1
    percentages = {d: round((c / total) * 100, 1) for d, c in counts.items()}

    sorted_doshas = sorted(counts, key=counts.get, reverse=True)
    top = counts[sorted_doshas[0]]
    second = counts[sorted_doshas[1]]
    third = counts[sorted_doshas[2]]

    dominant = sorted_doshas[0] if top > 0 else ""
    secondary = ""
    classification = "single"

    all_within_one = (top - third) <= 1
    top_two_equal = top == second
    all_equal = top == second == third

    if all_equal or (all_within_one and top > 0):
        classification = "tridoshic"
    elif top_two_equal and second > third:
        classification = "dual"
        secondary = sorted_doshas[1]
    elif second == third and second > 0:
        classification = "dual"
        secondary = sorted_doshas[1]
    elif (top - second) <= 1 and second > third:
        classification = "dual"
        secondary = sorted_doshas[1]

    return {
        "scores": counts,
        "percentages": percentages,
        "dominant_dosha": dominant,
        "secondary_dosha": secondary,
        "classification": classification,
        "quiz_version": QUIZ_VERSION,
    }
