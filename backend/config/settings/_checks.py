"""Startup checks for non-dev environments: refuse placeholder or weak secrets."""

from django.core.exceptions import ImproperlyConfigured

_PLACEHOLDERS = {"", "change-me", "changeme", "secret", "dev-token", "insecure-dev-key"}


def require_strong_secrets(**secrets: str) -> None:
    weak = [name for name, value in secrets.items() if value.strip().lower() in _PLACEHOLDERS or len(value) < 32]
    if weak:
        raise ImproperlyConfigured(
            f"Set strong random values (32+ characters) in the environment for: {', '.join(weak)}"
        )
