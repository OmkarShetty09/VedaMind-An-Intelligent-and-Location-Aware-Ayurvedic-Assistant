from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


def issue_tokens(user):
    """Return (access_str, refresh_str) for a user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def set_refresh_cookie(response, refresh_str):
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        refresh_str,
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=settings.REFRESH_COOKIE_PATH,
    )
    return response


def clear_refresh_cookie(response):
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path=settings.REFRESH_COOKIE_PATH)
    return response


def blacklist_refresh(refresh_str):
    """Revoke a refresh token (logout / rotation-orphan cleanup)."""
    try:
        RefreshToken(refresh_str).blacklist()
    except TokenError:
        pass
