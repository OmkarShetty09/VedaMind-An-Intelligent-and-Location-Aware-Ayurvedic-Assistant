def apply_filters(query: str, user_context: dict) -> dict:
    """Metadata filters derived from context. e.g. prefer clinical evidence
    when a modern drug is mentioned in the user's medications."""
    filters = {}
    meds = user_context.get("medications") or []
    if meds:
        filters["evidence_level"] = "modern_clinical"
    return filters