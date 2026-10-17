from rest_framework import serializers

from .models import DoshaAssessment, DoshaInfo, DoshaProfile, QuizQuestion


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


class DoshaInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoshaInfo
        fields = ["dosha", "label", "element", "tagline", "description"]


class QuizQuestionSerializer(serializers.ModelSerializer):
    # Only the option texts go to the client; which dosha an option scores stays server-side.
    options = serializers.SerializerMethodField()

    class Meta:
        model = QuizQuestion
        fields = ["key", "section", "prompt", "options"]

    def get_options(self, obj):
        return [o["text"] for o in obj.options]


class DoshaSubmitSerializer(serializers.Serializer):
    """answers = {question_key: option_index} for every active quiz question."""

    answers = serializers.DictField(required=True)

    def validate_answers(self, value):
        questions = {q.key: q for q in QuizQuestion.objects.filter(active=True)}
        if not questions:
            raise serializers.ValidationError("The quiz has no active questions.")
        unknown = sorted(set(value) - set(questions))
        if unknown:
            raise serializers.ValidationError(f"Unknown question(s): {', '.join(unknown)}.")
        missing = sorted(set(questions) - set(value))
        if missing:
            raise serializers.ValidationError(f"Please answer every question (missing: {', '.join(missing)}).")
        normalized = {}
        for key, index in value.items():
            options = questions[key].options
            if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(options):
                raise serializers.ValidationError(f"Answer for '{key}' must be an option number 0-{len(options) - 1}.")
            normalized[key] = {"dosha": options[index]["dosha"], "value": 1, "option": index}
        return normalized
