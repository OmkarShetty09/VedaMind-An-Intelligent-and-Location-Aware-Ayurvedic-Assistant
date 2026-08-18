import re
from zoneinfo import available_timezones

from django.core.exceptions import ValidationError


def validate_timezone(value: str) -> None:
    if value not in available_timezones():
        raise ValidationError(f"Unknown timezone: {value}")


_DOSAGE_RE = re.compile(r"^\d{1,4}(\.\d+)?\s*(mg|g|mcg|ml|tsp|drop|tab|caps)?$")


def validate_dosage(value: str) -> None:
    if not _DOSAGE_RE.match(value.strip()):
        raise ValidationError("Dosage must look like '5 mg', '1 tsp', etc.")
