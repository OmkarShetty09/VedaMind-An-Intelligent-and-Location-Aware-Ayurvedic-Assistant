import uuid


def make_correlation_id() -> str:
    return uuid.uuid4().hex


def request_correlation_id(request) -> str:
    return getattr(request, "correlation_id", "")
