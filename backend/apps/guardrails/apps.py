from django.apps import AppConfig


class GuardrailsConfig(AppConfig):
    name = "apps.guardrails"
    verbose_name = "Guardrails"

    def ready(self):
        from django.db.models.signals import post_delete, post_save

        from .alias_graph import reset_graph_cache
        from .models import DrugAlias, HerbAlias

        def _invalidate(**_kwargs):
            reset_graph_cache()

        for model in (HerbAlias, DrugAlias):
            post_save.connect(_invalidate, sender=model, dispatch_uid=f"guardrail-cache-{model.__name__}-save")
            post_delete.connect(_invalidate, sender=model, dispatch_uid=f"guardrail-cache-{model.__name__}-delete")
