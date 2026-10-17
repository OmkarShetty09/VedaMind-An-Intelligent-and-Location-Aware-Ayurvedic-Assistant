from django.contrib import admin

from .models import DoshaAssessment, DoshaInfo, DoshaProfile, QuizQuestion


@admin.register(DoshaProfile)
class DoshaProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "dominant_dosha", "updated_at"]


@admin.register(DoshaAssessment)
class DoshaAssessmentAdmin(admin.ModelAdmin):
    list_display = ["user", "quiz_version", "created_at"]


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ["order", "prompt", "section", "active"]
    list_editable = ["active"]
    list_display_links = ["prompt"]
    ordering = ["order"]


@admin.register(DoshaInfo)
class DoshaInfoAdmin(admin.ModelAdmin):
    list_display = ["label", "element", "tagline"]
