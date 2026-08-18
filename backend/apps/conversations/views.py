import logging

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.middleware.request_context import request_correlation_id
from apps.users.permissions import HasAcceptedDisclaimer

from .models import Conversation, Message
from .serializers import ChatRequestSerializer, ConversationSerializer, MessageSerializer
from .services import build_context_bundle
from .streaming import stream_chat

logger = logging.getLogger(__name__)


class ChatView(APIView):
    """POST /api/v1/chat - persists the user turn, streams the RAG answer via SSE."""

    permission_classes = [permissions.IsAuthenticated, HasAcceptedDisclaimer]
    throttle_scope = "chat"

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.get("session_id"):
            conversation = Conversation.objects.filter(id=data["session_id"], user=request.user).first()
            if conversation is None:
                return Response(
                    {"error": {"code": "not_found", "message": "Conversation not found."}},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            conversation = Conversation.objects.create(user=request.user)

        user_message = Message.objects.create(
            conversation=conversation, role="user", content=data["message"]
        )
        request.conversation = conversation
        request.message = user_message

        history = list(
            Message.objects.filter(conversation=conversation, role__in=("user", "assistant"))
            .order_by("-created_at")[:8]
        )[::-1]
        bundle = build_context_bundle(request.user, history)

        correlation_id = request_correlation_id(request)
        return stream_chat(
            user_id=str(request.user.id),
            user_message=data["message"],
            context_bundle=bundle,
            session_id=conversation.id,
            correlation_id=correlation_id,
            user_message_id=user_message.id,
        )


class SessionListView(generics.ListAPIView):
    """GET /api/v1/chat/sessions - paged conversation list."""

    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user, deleted_at__isnull=True)


class SessionDetailView(generics.RetrieveDestroyAPIView):
    """GET/DELETE /api/v1/chat/sessions/{id} - full history; soft delete."""

    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        conversation = self.get_object()
        messages = Message.objects.filter(conversation=conversation).select_related("guardrail_decision")
        return Response(
            {
                "id": conversation.id,
                "title": conversation.title,
                "messages": MessageSerializer(messages, many=True).data,
            }
        )

    def destroy(self, request, *args, **kwargs):
        conversation = self.get_object()
        conversation.deleted_at = timezone.now()
        conversation.save(update_fields=["deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
