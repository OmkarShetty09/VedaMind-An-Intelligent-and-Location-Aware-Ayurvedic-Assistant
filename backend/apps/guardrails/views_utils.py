"""Shared helpers for guardrail views (kept import-light for the RAG client path)."""


def context_flags(raw: dict) -> dict:
    """Normalize user context into boolean safety flags.

    Flags may be sent explicitly or implied by the user's self-reported conditions.
    """
    conditions = {str(c).lower() for c in raw.get("conditions", []) if c}
    raw_flags = {k: raw.get(k) for k in ("pregnancy", "pediatric", "renal")}
    flags = {k: bool(v) for k, v in raw_flags.items()}
    flags["pregnancy"] |= any("pregnan" in c for c in conditions)
    flags["pediatric"] |= any("child" in c or "pediatric" in c for c in conditions)
    flags["renal"] |= any("kidney" in c or "renal" in c or "ckd" in c for c in conditions)
    flags["diabetes"] = bool({"diabetes", "type 2 diabetes", "type 1 diabetes"} & conditions) or any(
        "diabet" in c for c in conditions
    )
    return flags
