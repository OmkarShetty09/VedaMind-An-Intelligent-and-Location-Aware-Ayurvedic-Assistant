# VedaMind — An Intelligent and Location-Aware Ayurvedic Assistant

RAG-powered Ayurvedic wellness guidance with a deterministic herb–drug interaction guardrail and a location/weather/season-aware Dinacharya (daily routine) engine.

> **Not a medical device.** VedaMind provides general wellness education. It never diagnoses, prescribes, or approves drug–herb combinations.

## Services

| Service | Dir | Stack |
|---|---|---|
| Backend (API gateway) | `backend/` | Django 5 + DRF, JWT (rotating refresh), Celery |
| RAG pipeline | `rag/` | FastAPI, pgvector + tsvector hybrid retrieval, BGE rerank |
| Frontend | `frontend/` | React 18 + Vite + Redux Toolkit |
| Infra | `infra/` | Docker Compose (dev + prod), Nginx, backups, Prometheus + Grafana |

## Quickstart (dev)

```bash
make setup        # copy .env, start postgres+redis, migrate, seed
make dev          # build + run all services
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1
- RAG API: http://localhost:8001/docs
- Health: http://localhost:8000/healthz

## Production

```bash
make deploy       # blue-green deploy via infra/scripts/deploy.sh
make backup       # pg_dump to infra/backups/
make secrets      # generate secrets (idempotent)
```

Prod compose: `infra/docker-compose.prod.yml` (includes nginx, monitoring, all services).

## Structure

```
backend/
  apps/           # users, dosha_profiles, guardrails, interactions_log,
                  # conversations, dinacharya, weather, core
  config/         # Django settings (base/dev/prod/staging), Celery, URLs
  docker/         # Dockerfile, entrypoint, gunicorn config
  requirements/   # base, dev, prod

rag/
  app/
    core/         # orchestrator, context, citations, errors, tracing
    llm/          # router (Gemini→Groq→Ollama), providers, streaming, cache
    retrieval/    # hybrid search, reranker, pgvector/milvus stores
    ingestion/    # chunker, loader, indexer, embeddings, manifest
    guardrails/   # rules client, jailbreak detector, secondary check
    security/     # input sanitizer, prompt injection defense
    prompts/      # Jinja2 templates
    evaluation/   # harness, metrics, eval scripts
    api/v1/       # chat, retrieve, ingest, health, guardrail endpoints
  tests/          # pipeline, chunker, reranker, streaming, security tests

frontend/
  src/
    api/          # auth, chat, dosha, dinacharya, weather
    components/   # chat, common, dinacharya, dosha, layout, location
    contexts/     # auth, location, theme, toast
    hooks/        # useAuth, useChat, useSSE, useGeolocation, etc.
    pages/        # Chat, Dinacharya, DoshaAssessment, Home, Login, etc.
    store/        # Redux slices: auth, chat, dosha, dinacharya, guardrail, location
    utils/        # SSE client, formatters

infra/
  docker-compose.yml          # dev (root)
  docker-compose.prod.yml     # prod (includes monitoring)
  nginx/                      # reverse proxy, rate limiting, SSE streaming
  monitoring/                 # prometheus.yml, alerts.yml
  postgres/                   # init scripts (pgvector + pg_trgm extensions)
  scripts/                    # backup, restore, seed, secrets, wait-for-it
```

## Key Make Targets

| Target | What it does |
|---|---|
| `make setup` | Bootstrap: .env, postgres, redis, migrate, seed |
| `make dev` | Run all services with live reload |
| `make test` | Run backend + rag + frontend tests |
| `make lint` | Ruff (Python) + ESLint (JS) |
| `make eval` | Run RAG retrieval + guardrail evaluations |
| `make backup` | pg_dump with compression |
| `make deploy` | Blue-green deploy with health check |
| `make secrets` | Generate all secrets (idempotent) |
