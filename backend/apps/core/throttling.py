from django.conf import settings
from rest_framework.throttling import AnonRateThrottle as DRFAnonRateThrottle
from rest_framework.throttling import UserRateThrottle


def _is_rag_service(request) -> bool:
    """The internal RAG service authenticates with X-RAG-Admin-Token, not a JWT."""
    token = request.headers.get("X-RAG-Admin-Token")
    return bool(token) and token == settings.RAG_ADMIN_TOKEN


class AnonRateThrottle(DRFAnonRateThrottle):
    scope = "anon"

    def allow_request(self, request, view):
        # Service-to-service calls would otherwise share one anonymous bucket for all users.
        if _is_rag_service(request):
            return True
        return super().allow_request(request, view)


class AuthedRateThrottle(UserRateThrottle):
    scope = "authed"


class ChatRateThrottle(UserRateThrottle):
    scope = "chat"


class GuardrailRateThrottle(UserRateThrottle):
    scope = "guardrail"

    def allow_request(self, request, view):
        if _is_rag_service(request):
            return True
        return super().allow_request(request, view)
