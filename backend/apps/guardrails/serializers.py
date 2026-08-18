from rest_framework import serializers

from .models import HerbAlias, InteractionRule, RuleVersion


class InteractionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionRule
        fields = [
            "id", "herb_a", "herb_b_or_drug", "direction", "interaction_type",
            "mechanism", "recommendation", "severity", "evidence",
            "dose_threshold", "context_tag", "source_uri", "active",
        ]
        read_only_fields = ["id"]


class HerbAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = HerbAlias
        fields = ["id", "canonical_herb", "alias", "language", "confidence"]


class RuleVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleVersion
        fields = ["version", "sha256", "activated_at", "steward"]


class InteractionCheckSerializer(serializers.Serializer):
    """Guardrail check input: raw text OR explicit entity lists."""

    text = serializers.CharField(max_length=4000, required=False, allow_blank=True)
    entities = serializers.ListField(child=serializers.CharField(max_length=120), required=False)
    context = serializers.DictField(child=serializers.CharField(), required=False)
    doses = serializers.DictField(child=serializers.CharField(), required=False)
    conversation_id = serializers.UUIDField(required=False)
    message_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        if not attrs.get("text") and not attrs.get("entities"):
            raise serializers.ValidationError("Provide either 'text' or 'entities'.")
        return attrs
