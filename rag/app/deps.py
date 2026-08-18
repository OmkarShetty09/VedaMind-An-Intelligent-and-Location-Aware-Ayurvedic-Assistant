from fastapi import Header, HTTPException

from app.config import get_settings

settings = get_settings()


def require_admin_token(x_rag_admin_token: str = Header(...)) -> str:
    """Internal service: every RAG call must present the admin token from Django."""
    if x_rag_admin_token != settings.rag_admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")
    return x_rag_admin_token