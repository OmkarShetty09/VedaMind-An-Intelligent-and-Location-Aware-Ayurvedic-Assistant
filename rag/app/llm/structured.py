"""JSON-mode completions for structured extraction and grounding verification."""

import json
import logging

from . import router

logger = logging.getLogger("rag.llm.structured")


def complete_json(messages: list[dict], tier: str = "cheap") -> dict:
    raw = router.complete(messages, tier=tier, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Provider returned non-JSON for structured call; len=%s", len(raw))
        # strip code fences as a last resort
        cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(cleaned)