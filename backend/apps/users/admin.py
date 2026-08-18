from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserCondition, UserMedication


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "name", "consent_accepted", "is_active"]
    search_fields = ["email", "name"]
    list_filter = ["is_active", "is_staff", "is_superuser", "consent_accepted"]
    filter_horizontal = ()
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("name", "timezone", "consent_accepted", "consent_version")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "name", "password1", "password2")}),)


@admin.register(UserMedication)
class UserMedicationAdmin(admin.ModelAdmin):
    list_display = ["user", "free_text", "active"]
    list_filter = ["active"]


@admin.register(UserCondition)
class UserConditionAdmin(admin.ModelAdmin):
    list_display = ["user", "condition", "severity", "active"]
    list_filter = ["active", "condition"]
