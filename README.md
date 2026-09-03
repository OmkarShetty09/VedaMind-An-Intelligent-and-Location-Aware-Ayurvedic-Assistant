# VedaMind — An Intelligent and Location-Aware Ayurvedic Assistant

RAG-powered Ayurvedic wellness guidance with a deterministic herb–drug interaction guardrail, location/weather/season-aware Dinacharya (daily routine) engine, and personalized dosha-aware chat.

> **Not a medical device.** VedaMind provides general wellness education. It never diagnoses, prescribes, or approves drug–herb combinations.

## Features

- **Dosha-gated chat** — mandatory Prakriti assessment before first message; dosha badge persists in chat header
- **Location & season context** — every message carries geolocation + weather; Ritucharya rules applied automatically
- **Herb-drug interaction guardrails** — deterministic rules engine + LLM secondary check; blocks/cautions rendered as red/amber banners
- **Anti-hallucination** — every claim traceable to retrieved classical sources; collapsible citation chips; low-confidence answers styled distinctly
- **Clarifying questions** — if user hasn't disclosed medications, assistant asks before recommending herbs
- **Multi-tier LLM failover** — Gemini → Groq → Ollama with streaming, caching, and token budgeting
- **Comprehensive knowledge base** — 375+ chunks from classical texts (Charaka, Sushruta, Ashtanga Hridaya) and Ayurwiki (5,400+ articles covering herbs, medicines, yoga, concepts, traditions)

## Services

| Service | Dir | Stack |
|---|---|---|
| Backend (API gateway) | `backend/` | Django 5 + DRF, JWT (rotating refresh), Celery |
| RAG pipeline | `rag/` | FastAPI, pgvector + tsvector hybrid retrieval, BGE rerank |
| Frontend | `frontend/` | React 18 + Vite + Redux Toolkit |
| Infra | `infra/` | Docker Compose (dev + prod), Nginx, backups, Prometheus + Grafana |

## Quickstart

### With Docker Desktop

```powershell
# 1. Start Docker Desktop (from Start menu)
# 2. Bootstrap
cp .env.example .env
docker compose up -d postgres redis
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo_data
docker compose exec backend python manage.py create_superuser
# 3. Run all services
docker compose up --build
```

### Without Docker (local)

Prerequisites: PostgreSQL 16 + pgvector, Redis, Python 3.12, Node.js 20.

```powershell
# 1. Database
createdb vedamind
psql vedamind -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql vedamind -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"

# 2. Backend
cd backend; pip install -r requirements/dev.txt
python manage.py migrate; python manage.py seed_demo_data
python manage.py create_superuser; python manage.py runserver

# 3. RAG (new terminal)
cd rag; pip install -r requirements/dev.txt
uvicorn app.main:app --reload --port 8001

# 4. Frontend (new terminal)
cd frontend; npm ci; npm run dev
```

### Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1
- RAG API docs: http://localhost:8001/docs
- Health check: http://localhost:8000/healthz

## Chat Flow

1. **First visit** → DoshaAssessmentPage (multi-step quiz, 8 questions, progress bar)
2. **After dosha profile** → ChatPage unlocks; dosha badge shown in header
3. **Every message** → location/weather/season attached automatically
4. **Before response** → guardrail checks herb-drug interactions; red/amber banner if flagged
5. **If meds unknown** → assistant asks "Are you on any medication?" with quick-reply chips
6. **Response** → citations expandable below message; low-confidence answers styled in amber

## Production

```powershell
# Blue-green deploy
bash infra/scripts/deploy.sh

# Backup
bash infra/scripts/backup.sh

# Generate secrets (idempotent)
bash infra/scripts/generate-secrets.sh
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
    prompts/      # Jinja2 templates (system_grounded.j2, refusal.j2)
    evaluation/   # harness, metrics, eval scripts
    api/v1/       # chat, retrieve, ingest, health, guardrail endpoints
  tests/          # pipeline, chunker, reranker, streaming, security tests

frontend/
  src/
    api/          # auth, chat, dosha, dinacharya, weather
    components/   # chat (ChatWindow, MessageBubble, GuardrailBanner, SourceCitation),
                  # dosha (Quiz, ResultChart, ScaleBar), layout, location
    contexts/     # auth, location, theme, toast
    hooks/        # useAuth, useChat, useSSE, useGeolocation, useWeather
    pages/        # Chat, Dinacharya, DoshaAssessment, Home, Login, etc.
    store/        # Redux slices: auth, chat, dosha, dinacharya, guardrail, location

infra/
  docker-compose.prod.yml     # prod (includes monitoring)
  nginx/                      # reverse proxy, rate limiting, SSE streaming
  monitoring/                 # prometheus.yml, alerts.yml
  postgres/                   # init scripts (pgvector + pg_trgm extensions)
  scripts/                    # backup, restore, seed, secrets

data/
  raw/                        # Corpus sources for RAG ingestion
    charaka_samhita/          # Classical text (44 chunks)
    sushruta_samhita/         # Classical text (12 chunks)
    ashtanga_hridaya/         # Classical text (12 chunks)
    bhavaprakasha/            # Herb pharmacopeia (10 chunks)
    nighantus/                # Herb pharmacopeia (10 chunks)
    clinical_evidence/        # Modern clinical studies (10 chunks)
    ayurwiki_herbs/           # 20 curated herbs from Ayurwiki (128 chunks)
    ayurwiki_medicines/       # 10 formulations from Ayurwiki (16 chunks)
    ayurwiki_concepts/        # Core concepts from Ayurwiki (50 chunks)
    ayurwiki_yoga/            # Asanas & pranayama from Ayurwiki (71 chunks)
    ayurwiki_traditions/      # Therapies from Ayurwiki (12 chunks)
  processed/                  # Generated chunks, index manifest
  evaluation/                 # Test queries for retrieval quality
```

## Testing

```powershell
# Backend
cd backend; pytest

# RAG
cd rag; pytest

# Frontend
cd frontend; npm test
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register` | — | Create account |
| POST | `/api/v1/auth/login` | — | Login (JWT cookie) |
| GET | `/api/v1/users/me` | JWT | Current user profile |
| POST | `/api/v1/dosha/assess` | JWT | Submit dosha quiz |
| GET | `/api/v1/dosha/profile` | JWT | Get dosha profile |
| POST | `/api/v1/chat/` | JWT | Send message (SSE stream) |
| GET | `/api/v1/chat/sessions` | JWT | List conversations |
| POST | `/api/v1/guardrails/check` | JWT | Check herb-drug interaction |
| GET | `/api/v1/weather/current` | JWT | Current weather |
| POST | `/api/v1/dinacharya/recommend` | JWT | Generate daily routine |
| GET | `/healthz` | — | Health check |
