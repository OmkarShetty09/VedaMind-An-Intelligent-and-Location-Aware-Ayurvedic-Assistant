from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    """Allow access only to the authenticated user's own resources."""

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class HasAcceptedDisclaimer(BasePermission):
    """Consent gate: no herb-specific output before informed consent."""

    message = "Please accept the disclaimer before continuing."

    def has_permission(self, request, view):
        if not request.user or request.user.is_anonymous:
            return False
        # Cache the flag briefly to avoid a DB hit per request.
        cached = cache.get(f"consent:{request.user.id}")
        if cached is None:
            cached = request.user.consent_accepted
            cache.set(f"consent:{request.user.id}", cached, 60)
        return cached


class HasRAGAdminToken(BasePermission):
    """Internal RAG service -> Django. Not used for user endpoints."""

    def has_permission(self, request, view):
        token = request.headers.get("X-RAG-Admin-Token")
        return bool(token and token == settings.RAG_ADMIN_TOKEN)
