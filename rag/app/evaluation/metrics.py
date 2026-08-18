"""Metrics for the eval harness (faithfulness + coverage)."""


def faithful(claims: list[dict]) -> float:
    """claims: [{sentence, supported}] -> fraction supported."""
    if not claims:
        return 0.0
    return sum(1 for c in claims if c.get("supported")) / len(claims)


def coverage(retrieved_ids: set, relevant_ids: set) -> float:
    """Fraction of the gold relevant chunks that were retrieved."""
    if not relevant_ids:
        return 0.0
    return len(retrieved_ids & relevant_ids) / len(relevant_ids)


def precision(retrieved_ids: set, relevant_ids: set) -> float:
    if not retrieved_ids:
        return 0.0
    return len(retrieved_ids & relevant_ids) / len(retrieved_ids)


def answerable(answer: str) -> bool:
    """A refusal/irrelevant answer scores 0 for usability."""
    return bool(answer.strip())