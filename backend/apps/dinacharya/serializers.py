from rest_framework import serializers

from .models import DinacharyaRecommendation, RoutineActivity


class RoutineActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineActivity
        fields = [
            "time_of_day", "start", "end", "title", "description",
            "reasons", "citations", "dosha_target", "order",
        ]


class DinacharyaSerializer(serializers.ModelSerializer):
    activities = RoutineActivitySerializer(many=True, read_only=True)

    class Meta:
        model = DinacharyaRecommendation
        fields = ["date", "season", "engine_version", "inputs_snapshot", "generated_at", "activities"]
