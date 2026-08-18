from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core import orchestrator
from app.core.errors import PipelineError
from app.llm import streaming

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    message_id: str | None = None
    context: dict = {}


@router.post("/chat")
def chat(payload: ChatRequest, request: Request):
    """POST /chat -> SSE stream. Called by Django (admin-token protected)."""

    def gen():
        try:
            yield from orchestrator.run(
                payload.message,
                payload.context,
                conversation_id=payload.session_id,
                message_id=payload.message_id,
            )
        except PipelineError as exc:
            yield streaming.error_event(exc.code, exc.message)
        except Exception as exc:
            request.app.state.logger.exception("Unhandled pipeline error")
            yield streaming.error_event("internal", f"Unexpected pipeline failure: {type(exc).__name__}")

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )