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


class LocationPayloadSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=False)
    lon = serializers.FloatField(required=False)
    season = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    current_weather = serializers.DictField(required=False)


class ChatRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(max_length=8000, allow_blank=False)
    location = LocationPayloadSerializer(required=False)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value
