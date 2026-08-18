"""LLM judge for faithfulness scoring (used in generation eval, not binding)."""

from app.llm.structured import complete_json


def judge_answer(answer: str, passages: list[dict]) -> list[dict]:
    prompt = (
        "Return JSON ONLY: {\"claims\": [{\"sentence\": \"...\", \"supported\": true/false}]}. "
        "Judge each sentence of the answer against the passages.\n\nPASSAGES:\n"
        + "\n".join(p["content"] for p in passages)
        + "\n\nANSWER:\n" + answer
    )
    result = complete_json([{"role": "user", "content": prompt}], tier="cheap")
    return result.get("claims", [])