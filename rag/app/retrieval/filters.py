"""Metadata filters derived from context.

Supports source_type filtering for evidence classification:
- CLASSICAL: Charaka, Sushruta, Ashtanga Hridaya
- DRAVYAGUNA: herb property texts (Nighantus, Bhavaprakasha)
- MODERN_CLINICAL: RCTs, meta-analyses
- SAFETY: interaction rules (separate from RAG)
"""

# Source type preference rules based on question intent
_SOURCE_TYPE_PREFERENCES = {
    "herb_properties": ["DRAVYAGUNA", "CLASSICAL"],
    "treatment_protocol": ["CLASSICAL"],
    "clinical_evidence": ["MODERN_CLINICAL"],
    "safety": ["MODERN_CLINICAL", "SAFETY"],
}


def apply_filters(query: str, user_context: dict) -> dict:
    """Metadata filters derived from context.

    When medications are present, prefer modern clinical evidence.
    When no medications, prefer classical sources.
    """
    filters = {}
    meds = user_context.get("medications") or []
    conditions = user_context.get("conditions") or []

    if meds:
        # User is on medication: prefer clinical evidence for safety
        filters["source_type"] = "MODERN_CLINICAL"
    elif conditions:
        # User has conditions but no meds: prefer classical + clinical
        pass  # no filter; let hybrid search find from all sources
    else:
        # No meds, no conditions: prefer classical sources
        pass  # no filter

    return filters
