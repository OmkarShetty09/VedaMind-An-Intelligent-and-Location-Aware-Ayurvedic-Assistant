import pytest


@pytest.fixture(autouse=True)
def _isolated_cache_and_graph():
    """Throttle counters, the consent flag and the herb alias graph must not leak between tests."""
    from django.core.cache import cache

    from apps.guardrails.alias_graph import reset_graph_cache

    cache.clear()
    reset_graph_cache()
    yield
    cache.clear()
    reset_graph_cache()
