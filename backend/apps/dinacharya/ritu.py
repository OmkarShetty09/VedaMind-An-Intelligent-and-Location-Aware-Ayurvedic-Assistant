"""Ritucharya: the six classical seasons from date + hemisphere.

The calendar (start dates, labels) lives in data/ritu.json so the backend, the chat context and
the frontend all use one definition. Accurate within a few days; fine for wellness advice.
Southern hemisphere shifts by six months.
"""

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent / "data" / "ritu.json"


@lru_cache(maxsize=1)
def seasons() -> list[dict]:
    """Seasons ordered by start date within the year."""
    items = json.loads(_DATA.read_text(encoding="utf-8"))["seasons"]
    return sorted(items, key=lambda s: tuple(s["start"]))


def season_for(d: date, northern: bool = True) -> str:
    if not northern:
        d = (d + timedelta(days=183)).replace(year=d.year)
    ordered = seasons()
    result = ordered[-1]["key"]  # before the first start date we are still in the year's last ritu
    for item in ordered:
        if (d.month, d.day) >= tuple(item["start"]):
            result = item["key"]
    return result


def season_info(key: str) -> dict:
    """{"key", "label", "english", "emoji"} for a ritu key."""
    for item in seasons():
        if item["key"] == key:
            return {k: item[k] for k in ("key", "label", "english", "emoji")}
    return {"key": key, "label": key.title(), "english": key, "emoji": ""}
