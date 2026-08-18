import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    """Normalize every API error into {error: {code, message, fields?}}."""
    response = drf_exception_handler(exc, context)
    if response is None:
        logger.exception("Unhandled API error", exc_info=exc)
        return Response(
            {"error": {"code": "internal", "message": "An unexpected error occurred."}},
            status=500,
        )
    data = response.data
    message = None
    if isinstance(data, dict) and "detail" in data:
        message = data["detail"]
    response.data = {"error": {"code": getattr(exc, "default_code", "error"), "message": message, "fields": data}}
    return response
