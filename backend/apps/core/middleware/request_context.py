from apps.core.utils import make_correlation_id


def request_correlation_id(request):
    """Read the correlation id attached by the middleware (safe for any request)."""
    return getattr(request, "correlation_id", None) or make_correlation_id()


class RequestContextMiddleware:
    """Attach a correlation_id to every request for end-to-end tracing."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.correlation_id = request.headers.get("X-Correlation-ID") or make_correlation_id()
        response = self.get_response(request)
        response["X-Correlation-ID"] = request.correlation_id
        return response
