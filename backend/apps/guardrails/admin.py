from django.contrib import admin

from .models import HerbAlias, InteractionRule, RuleVersion


@admin.register(InteractionRule)
class InteractionRuleAdmin(admin.ModelAdmin):
    list_display = ["herb_a", "herb_b_or_drug", "severity", "evidence", "context_tag", "active"]
    list_filter = ["severity", "evidence", "active", "context_tag"]
    search_fields = ["herb_a", "herb_b_or_drug"]

    def save_model(self, request, obj, form, change):
        """Rules are versioned on every save: stamp the latest RuleVersion."""
        if not obj.rule_version:
            latest = RuleVersion.objects.order_by("-activated_at").first()
            if latest:
                obj.rule_version = latest
        super().save_model(request, obj, form, change)


@admin.register(HerbAlias)
class HerbAliasAdmin(admin.ModelAdmin):
    list_display = ["alias", "canonical_herb", "language", "confidence"]
    search_fields = ["alias", "canonical_herb"]


@admin.register(RuleVersion)
class RuleVersionAdmin(admin.ModelAdmin):
    list_display = ["version", "sha256", "activated_at", "steward"]
