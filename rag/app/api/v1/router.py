from fastapi import APIRouter, Depends

from app.deps import require_admin_token

from . import chat, guardrail, health, ingest, retrieve

router = APIRouter(dependencies=[Depends(require_admin_token)])

router.include_router(health.router, tags=["ops"])
router.include_router(ingest.router, tags=["ingest"])
router.include_router(retrieve.router, tags=["retrieve"])
router.include_router(guardrail.router, tags=["guardrail"])
router.include_router(chat.router, tags=["chat"])