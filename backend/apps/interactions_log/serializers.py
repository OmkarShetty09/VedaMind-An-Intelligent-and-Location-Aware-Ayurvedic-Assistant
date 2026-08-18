from rest_framework import serializers

from .models import ConsentRecord, GuardrailDecision


class GuardrailDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardrailDecision
        fields = [
            "id", "user", "conversation", "message", "correlation_id",
            "entities", "matched_rules", "severity", "decision",
            "reason_code", "engine_version", "llm_version", "created_at",
        ]


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = ["id", "disclaimer_version", "created_at"]
