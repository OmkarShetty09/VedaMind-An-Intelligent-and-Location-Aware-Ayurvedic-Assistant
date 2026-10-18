from rest_framework import serializers

from .models import DinacharyaRecommendation, RoutineActivity


class RoutineActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineActivity
        fields = [
            "time_of_day", "start", "end", "title", "description",
            "reasons", "citations", "dosha_target", "personalized", "order",
        ]


class DinacharyaSerializer(serializers.ModelSerializer):
    activities = RoutineActivitySerializer(many=True, read_only=True)
    season_info = serializers.SerializerMethodField()
    personalization = serializers.SerializerMethodField()

    class Meta:
        model = DinacharyaRecommendation
        fields = ["date", "season", "season_info", "personalization", "engine_version", "inputs_snapshot",
                  "generated_at", "activities"]

    def get_season_info(self, obj):
        from .ritu import season_info

        return season_info(obj.season)

    def get_personalization(self, obj):
        return (obj.inputs_snapshot or {}).get("personalization") or {"assessed": False}
