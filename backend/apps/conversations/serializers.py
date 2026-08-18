from rest_framework import serializers

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id", "role", "content", "source_citations",
            "guardrail_decision", "llm_model", "tokens", "created_at",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "updated_at"]


class ChatRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=False)
    message = serializers.CharField(max_length=8000, allow_blank=False)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value
