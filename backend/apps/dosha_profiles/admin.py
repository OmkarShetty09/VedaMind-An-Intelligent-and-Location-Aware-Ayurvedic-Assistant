from django.contrib import admin

from .models import DoshaAssessment, DoshaProfile


@admin.register(DoshaProfile)
class DoshaProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "dominant_dosha", "updated_at"]


@admin.register(DoshaAssessment)
class DoshaAssessmentAdmin(admin.ModelAdmin):
    list_display = ["user", "quiz_version", "created_at"]
