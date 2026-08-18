from django.contrib import admin

from .models import DinacharyaRecommendation, RoutineActivity


class RoutineActivityInline(admin.TabularInline):
    model = RoutineActivity
    extra = 0


@admin.register(DinacharyaRecommendation)
class DinacharyaRecommendationAdmin(admin.ModelAdmin):
    list_display = ["user", "date", "season", "engine_version", "generated_at"]
    inlines = [RoutineActivityInline]
