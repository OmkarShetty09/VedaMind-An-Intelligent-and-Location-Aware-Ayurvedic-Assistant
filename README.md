# VedaMind — An Intelligent and Location-Aware Ayurvedic Assistant

RAG-powered Ayurvedic wellness guidance with a deterministic herb–drug interaction guardrail and a location/weather/season-aware Dinacharya (daily routine) engine.

> **Not a medical device.** VedaMind provides general wellness education. It never diagnoses, prescribes, or approves drug–herb combinations. Read the legal + safety plan in `docs/` and `PLAN.md`.

## Services

| Service | Dir | Stack |
|---|---|---|
| Backend (API gateway) | `backend/` | Django 5 + DRF, JWT (rotating refresh), Celery |
| RAG pipeline | `rag/` | FastAPI, LangChain-core, pgvector + tsvector hybrid, BGE rerank |
| Frontend | `frontend/` | React 18 + Vite + Redux Toolkit |
| Infra | `infra/` | Docker Compose, Nginx, backups, monitoring |

## Quickstart (dev)

```bash
make setup        # copy .env, start postgres+redis, migrate, seed
make dev          # build + run all services
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1
- Health: http://localhost:8000/healthz

## Docs

- Full production plan: `PLAN.md`
- API contract: `docs/api-contract.md`
- Decisions: `docs/adr/`
- Data licensing: `docs/data-licensing.md`
- Runbooks: `docs/runbook/`