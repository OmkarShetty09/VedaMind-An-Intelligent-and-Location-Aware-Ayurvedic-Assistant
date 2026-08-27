from rest_framework import serializers

from .models import DoshaAssessment, DoshaProfile

_DOSHA_MAP = {0: "vata", 1: "pitta", 2: "kapha"}


class DoshaProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoshaProfile
        fields = ["id", "prakriti_scores", "vikriti_scores", "dominant_dosha", "secondary_dosha", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class DoshaAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoshaAssessment
        fields = ["id", "quiz_version", "answers", "results", "created_at"]
        read_only_fields = ["id", "quiz_version", "results", "created_at"]


class DoshaSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(required=True)

    def validate_answers(self, value):
        normalized = {}
        for key, val in value.items():
            if isinstance(val, dict):
                normalized[key] = val
            elif isinstance(val, int) and val in _DOSHA_MAP:
                normalized[key] = {"dosha": _DOSHA_MAP[val], "value": 1}
            else:
                raise serializers.ValidationError(
                    f"Answer for '{key}' must be a dict or an int (0=vata, 1=pitta, 2=kapha)."
                )
        return normalized
