from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.config import get_settings
from app.logging import setup_logging  # noqa: F401  (side-effect: configure logging)

settings = get_settings()

app = FastAPI(title="VedaMind RAG", version="0.1.0", docs_url="/docs", openapi_url=None if settings.env == "prod" else "/openapi.json")

# Internal-only service; CORS is disabled in prod.
if settings.env == "dev":
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    request.state.correlation_id = request.headers.get("X-Correlation-ID", "")
    response: Response = await call_next(request)
    response.headers["X-Correlation-ID"] = request.state.correlation_id
    return response


app.include_router(v1_router, prefix="/api/v1")


@app.get("/healthz", tags=["ops"])
def healthz():
    return {"status": "ok", "store": settings.vector_store, "env": settings.env}