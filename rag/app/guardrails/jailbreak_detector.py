import re

_RISK_PATTERNS = [
    r"ignore all (previous )?(instructions|guardrails|safety)",
    r"override.{0,30}(rules|guardrail|safety)",
    r"pretend you are a (doctor|physician|medical professional|therapist)",
    r"role ?play as",
    r"this is (hypothetical|fictional|for research)",
    r"in a simulation",
    r"tell me it.s safe",
    r"bypass",
    r"\u200b",  # zero-width space (obfuscation)
    r"let.s play",
    r"do not warn me",
]


class JailbreakDetector:
    def __init__(self, patterns: list[str] | None = None):
        self._compiled = [re.compile(p, re.IGNORECASE) for p in (patterns or _RISK_PATTERNS)]

    def scan(self, text: str) -> tuple[bool, str]:
        for pattern in self._compiled:
            if pattern.search(text):
                return True, pattern.pattern
        return False, ""


_detector = JailbreakDetector()


def is_high_risk(text: str) -> bool:
    return _detector.scan(text)[0]