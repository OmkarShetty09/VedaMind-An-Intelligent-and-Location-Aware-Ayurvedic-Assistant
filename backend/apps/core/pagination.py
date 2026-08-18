from rest_framework.pagination import CursorPagination as DRFCursorPagination


class CursorPagination(DRFCursorPagination):
    """Stable cursor pagination for history/session endpoints."""

    page_size = 25
    ordering = "-created_at"
