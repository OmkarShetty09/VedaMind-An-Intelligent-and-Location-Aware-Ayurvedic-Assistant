import re

_INSTRUCTION_PREFIXES = re.compile(
    r"^\s*(ignore|disregard|forget|override|skip|bypass|forget all previous|pretend|assume the role of)\b",
    re.IGNORECASE,
)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\u200b-\u200f\ufeff]")


def sanitize(text: str) -> str:
    """Strip control/invisible chars, instruction-like prefixes, and collapse whitespace."""
    text = _CONTROL_CHARS.sub("", text)
    text = _INSTRUCTION_PREFIXES.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:4000]