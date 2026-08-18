"""Structured-log tracing per pipeline step. Lightweight; OTel swap-in later."""

import logging
import time
from contextlib import contextmanager

logger = logging.getLogger("rag.pipeline")


@contextmanager
def span(name: str, **fields):
    start = time.monotonic()
    try:
        yield
    finally:
        duration_ms = (time.monotonic() - start) * 1000
        logger.info("span", extra={"step": name, "duration_ms": round(duration_ms, 1), **fields})