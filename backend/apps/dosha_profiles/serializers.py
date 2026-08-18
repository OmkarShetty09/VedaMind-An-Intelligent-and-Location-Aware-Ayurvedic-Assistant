from rest_framework import serializers

from .models import DoshaAssessment, DoshaProfile


class DoshaProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoshaProfile
        fields = ["id", "prakriti_scores", "vikriti_scores", "dominant_dosha", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class DoshaAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoshaAssessment
        fields = ["id", "quiz_version", "answers", "results", "created_at"]
        read_only_fields = ["id", "quiz_version", "results", "created_at"]


class DoshaSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(child=serializers.DictField(), required=True)
