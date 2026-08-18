"""Shared helpers for guardrail views (kept import-light for the RAG client path)."""


def context_flags(raw: dict) -> dict:
    """Normalize user context into boolean safety flags."""
    conditions = {str(c).lower() for c in raw.get("conditions", []) if c}
    raw_flags = {k: raw.get(k) for k in ("pregnancy", "pediatric", "renal")}
    flags = {k: bool(v) for k, v in raw_flags.items()}
    flags["diabetes"] = bool({"diabetes", "type 2 diabetes", "type 1 diabetes"} & conditions)
    return flags
