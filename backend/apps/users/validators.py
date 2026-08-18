import re

from django.core.exceptions import ValidationError


def validate_email(value: str) -> None:
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
        raise ValidationError("Enter a valid email address.")
