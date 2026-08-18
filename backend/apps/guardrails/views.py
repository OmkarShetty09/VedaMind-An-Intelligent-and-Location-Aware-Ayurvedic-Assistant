import logging

from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.views import APIView

from .alias_graph import get_default_graph
from .entity_extraction import extract_entities
from .models import InteractionRule
from .rules_engine import evaluate, fail_closed
from .serializers import (
    InteractionCheckSerializer,
    InteractionRuleSerializer,
)
from .views_logger import log_decision  # shared audit write
from .views_utils import context_flags

logger = logging.getLogger(__name__)


class RAGOrAuthenticated(permissions.BasePermission):
    """Accept a logged-in user OR a valid RAG service admin token.

    The RAG pipeline calls /check with X-RAG-Admin-Token and no JWT; the
    frontend calls it with a JWT. Both must reach the engine.
    """

    message = "Authentication required (JWT or RAG admin token)."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            return True
        return request.headers.get("X-RAG-Admin-Token") == settings.RAG_ADMIN_TOKEN


class InteractionCheckView(APIView):
    """POST /api/v1/guardrails/check

    The RAG pipeline calls this before every generation. Returns a decision
    that is binding: the RAG pipeline gates on it (Section 4).
    """

    permission_classes = [RAGOrAuthenticated]
    throttle_scope = "guardrail"

    def post(self, request):
        serializer = InteractionCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ctx_flags = context_flags(data.get("context", {}))

        entities = data.get("entities")
        if not entities and data.get("text"):
            extraction = extract_entities(data["text"], get_default_graph())
            herbs = [e.canonical for e in extraction.herbs]
            drugs = [e.canonical for e in extraction.drugs]
            ambiguous = extraction.ambiguous
        else:
            herbs = [e.lower() for e in (entities or [])]
            drugs = []
            ambiguous = []

        # Audit linkage when the RAG pipeline proxies a chat turn.
        if data.get("conversation_id") or data.get("message_id"):
            from apps.conversations.models import Conversation, Message

            request.conversation = Conversation.objects.filter(
                id=data.get("conversation_id")
            ).first()
            request.message = Message.objects.filter(
                id=data.get("message_id"), conversation=request.conversation
            ).first() if request.conversation else None

        try:
            result = evaluate(
                herbs=herbs,
                drugs=drugs,
                context=ctx_flags,
                doses=data.get("doses", {}),
                ambiguous=ambiguous,
            )
        except Exception as exc:  # fail closed - never pass on error
            logger.exception("Guardrail engine error: %s", exc)
            result = fail_closed(exc)

        log_decision(
            request=request,
            herbs=herbs,
            drugs=drugs,
            ambiguous=ambiguous,
            result=result,
        )
        return Response(result_to_payload(result))


class KnownInteractionsView(generics.ListAPIView):
    """GET /api/v1/guardrails/interactions/{herb} - user-facing "am I covered?"."""

    serializer_class = InteractionRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from .alias_graph import normalize

        key = normalize(self.kwargs["herb"])
        return InteractionRule.objects.filter(active=True, herb_a__iexact=key)


def result_to_payload(result):
    return {
        "decision": result.overall,
        "reason_code": result.reason_code,
        "engine_version": result.engine_version,
        "matches": [
            {
                "pair": m.pair,
                "severity": m.severity,
                "evidence": m.evidence,
                "decision": m.decision,
                "reason_code": m.reason_code,
                "recommendation": m.recommendation,
            }
            for m in result.matches
        ],
        "entities": result.entities,
    }


def Response(payload, status=200):
    from rest_framework.response import Response as DRFResponse

    return DRFResponse(payload, status=status)
