import re

_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "phone": re.compile(r"(\+?\d[\d\s\-().]{7,})"),
}


def redact(text: str) -> str:
    for pattern in _PATTERNS.values():
        text = pattern.sub("[REDACTED]", text)
    return text