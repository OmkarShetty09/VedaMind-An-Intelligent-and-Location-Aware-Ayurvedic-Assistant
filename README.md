# VedaMind — An Intelligent and Location-Aware Ayurvedic Assistant

> **Just want to run it?** See **[SETUP.md](SETUP.md)**: double-click `START-VedaMind.bat`, open <http://localhost:5173>.

RAG-powered Ayurvedic wellness guidance with a deterministic herb–drug interaction guardrail, a
location/weather/season-aware Dinacharya (daily routine) engine, and dosha-personalised chat.

> **Not a medical device.** VedaMind provides general wellness education. It never diagnoses,
> prescribes, or approves drug–herb combinations.

## Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Setup on Windows without Docker (recommended)](#setup-on-windows-without-docker-recommended)
4. [Setup with Docker Desktop](#setup-with-docker-desktop)
5. [Manual setup (macOS / Linux / your own PostgreSQL)](#manual-setup-macos--linux--your-own-postgresql)
6. [Demo walkthrough](#demo-walkthrough)
7. [Configuration (.env)](#configuration-env)
8. [Architecture](#architecture)
9. [Running the tests](#running-the-tests)
10. [Troubleshooting](#troubleshooting)
11. [API endpoints](#api-endpoints)
12. [Project structure](#project-structure)

## Features

- **Dosha assessment** — 11-question Prakriti quiz (+ informed-consent screen) before the first chat; result chart and dosha badge.
- **Grounded RAG chat** — hybrid retrieval (pgvector dense + Postgres full-text) over 375 chunks from classical texts
  (Charaka, Sushruta, Ashtanga Hridaya, Bhavaprakasha, Nighantus) and Ayurwiki; every claim carries an `[S#]` citation
  you can click; answers stream token-by-token.
- **Herb–drug interaction guardrail** — deterministic rules engine (backend) checks the question *and the user's saved
  medications/conditions* before anything is generated; blocks / cautions show as red / amber banners with the matched
  pair and the rule's recommendation.
- **Clarifying questions** — before recommending herbs to someone who hasn't disclosed medications, the assistant asks
  first (with quick-reply buttons).
- **Location & season context** — browser location → Open-Meteo weather + Ritu (season); used in answers and routines.
- **Dinacharya engine** — today's routine computed from local sunrise/sunset, season, weather and dosha, with classical citations.
- **LLM failover** — Gemini (primary) → Groq (live fallback) → Ollama (optional local fallback); answer cache in Redis.
- **Conversation history** — saved per user; reopen or delete past chats.

## Requirements

| What | Version | Notes |
|---|---|---|
| Windows 10/11 | — | macOS/Linux work with Docker or the manual steps |
| Python | **3.12, 3.13 or 3.14** | tested on 3.12.10 and 3.14.6. Tick *“Add python.exe to PATH”* in the installer |
| Node.js | **20 or newer** (LTS) | tested on 24.18 |
| Git | any | to clone the repo |
| **Gemini API key** | free | **required** — answers *and* the knowledge-base embeddings: <https://aistudio.google.com/apikey> |
| Groq API key | free | recommended — used automatically when Gemini is busy (503/429): <https://console.groq.com/keys> |
| Internet | — | LLM APIs, weather (Open-Meteo), reverse geocoding (OpenStreetMap) |

PostgreSQL 16 + pgvector and Redis are also needed; the Windows scripts below provide both
**without Docker and without admin rights**.

---

## Setup on Windows without Docker (recommended)

**Easiest:** double-click **`START-VedaMind.bat`** in the project folder. The first time, it installs everything and
opens `.env` in Notepad for your `GEMINI_API_KEY`; then it starts the app and opens <http://localhost:5173>.
Double-click **`STOP-VedaMind.bat`** to stop. The first time you also need to build the knowledge base once:
`powershell -ExecutionPolicy Bypass -File scripts\windows\ingest.ps1`.

The same steps by hand:

Open **PowerShell** in the project folder (`Shift + right-click` the folder → *Open PowerShell window here*).

```powershell
# 1. One-time install: Python virtualenvs, packages, npm modules, creates .env
powershell -ExecutionPolicy Bypass -File scripts\windows\setup.ps1

# 2. Put your API keys in .env (opens Notepad). Set GEMINI_API_KEY=... and GROQ_API_KEY=...
notepad .env

# 3. Start everything: PostgreSQL + pgvector, Redis, migrations, demo data, backend, RAG, frontend
powershell -ExecutionPolicy Bypass -File scripts\windows\start.ps1

# 4. ONE TIME ONLY: build the knowledge base (~5 min on the free Gemini tier; it retries automatically)
powershell -ExecutionPolicy Bypass -File scripts\windows\ingest.ps1
```

Then open **<http://localhost:5173>**.

- `start.ps1` opens three terminal windows (backend, RAG, frontend). Keep them open while you use the app.
- Next time, only run step 3. The database and knowledge base are kept in `.localdev\` (git-ignored).
- Stop everything: `powershell -ExecutionPolicy Bypass -File scripts\windows\stop.ps1`
- Ports 8000 / 8001 / 5173 busy (another project running)? Use other ports:
  `start.ps1 -BackendPort 8010 -RagPort 8011 -FrontendPort 5180` (and the same options for `stop.ps1`).
- Already have PostgreSQL (with pgvector) and Redis installed? Point `.env` at them and run `start.ps1 -SkipInfra`.

**Accounts:** register your own at `/register`, or use the demo user `DEMO_USER_EMAIL` / `DEMO_USER_PASSWORD`.
Django admin: <http://localhost:5173/admin> with `DEMO_EMAIL` / `DEMO_PASSWORD`. All four come from `.env`
(defaults: admin `admin@vedamind.local` / `VedaMind@Admin123`, demo `demo@vedamind.local` / `VedaMind@Demo123`;
change them in `.env`, `start.ps1` prints the current ones). Nothing is hardcoded in the code.

**Editing content without touching code** (Django admin → log in with the admin account above):

| Admin section | What it controls |
|---|---|
| Dosha Profiles → Quiz questions / Dosha info | The assessment questions, which dosha each option scores, result descriptions |
| Dinacharya → Routine templates | Every routine activity: timing (sunrise/sunset/clock + offsets), text, citations, season / dosha variations, heat-only items |
| Conversations → Chat suggestions | Starter questions on an empty chat |
| Guardrails → Interaction rules / Herb aliases / Drug aliases | The safety rules, herb names and drug names/brands/classes (changes apply immediately) |

The season calendar is `backend/apps/dinacharya/data/ritu.json`; the starting content is in each app's `data/` folder.

<details>
<summary>What the scripts do (if you prefer to run the commands yourself)</summary>

`infra.ps1` installs the [`pgserver`](https://pypi.org/project/pgserver/) Python package (PostgreSQL 16.2 + pgvector 0.6
binaries) into `.localdev\pgvenv`, creates a cluster in `.localdev\pgdata`, the `vedamind` role/database and the
`vector` extension, and downloads the portable Redis build from
[redis-windows](https://github.com/redis-windows/redis-windows). Then, in three terminals:

```powershell
cd backend; .\.venv\Scripts\python manage.py migrate; .\.venv\Scripts\python manage.py seed_demo_data
.\.venv\Scripts\python manage.py create_superuser; .\.venv\Scripts\python manage.py runserver 127.0.0.1:8000
cd rag;     .\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
cd frontend; npm run dev
cd rag;     .\.venv\Scripts\python -m app.ingestion ingest      # once
```
</details>

---

## Setup with Docker Desktop

Needs Docker Desktop (WSL 2 backend). Everything runs in containers.

```powershell
copy .env.example .env          # then set GEMINI_API_KEY / GROQ_API_KEY in .env
docker compose up -d --build    # postgres, redis, backend (runs migrations), rag, frontend, celery
docker compose exec backend python manage.py seed_demo_data
docker compose exec backend python manage.py create_superuser
docker compose exec rag python -m app.ingestion ingest     # once, ~5 min
```

Open <http://localhost:5173>. Logs: `docker compose logs -f backend rag`. Stop: `docker compose down`
(add `-v` to also delete the database).

---

## Manual setup (macOS / Linux / your own PostgreSQL)

1. **PostgreSQL 16 with pgvector** (`brew install postgresql@16 pgvector`, `apt install postgresql-16-pgvector`, or the
   `pgvector/pgvector:pg16` image) and **Redis 7+**. Create the database (as the postgres superuser):
   ```sql
   CREATE ROLE vedamind LOGIN CREATEDB PASSWORD 'vedamind';
   CREATE DATABASE vedamind OWNER vedamind;
   \c vedamind
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
2. `cp .env.example .env` and set the API keys (and the DB password in `POSTGRES_PASSWORD` **and** `DATABASE_URL`).
3. Backend:
   ```bash
   cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements/dev.txt
   .venv/bin/python manage.py migrate && .venv/bin/python manage.py seed_demo_data && .venv/bin/python manage.py create_superuser
   .venv/bin/python manage.py runserver 127.0.0.1:8000
   ```
4. RAG (new terminal): `cd rag && python3 -m venv .venv && .venv/bin/pip install -r requirements/dev.txt && .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001`
5. Knowledge base (once): `cd rag && .venv/bin/python -m app.ingestion ingest`
6. Frontend (new terminal): `cd frontend && npm ci && npm run dev` → <http://localhost:5173>

---

## Demo walkthrough

A 5-minute script that shows every feature:

1. **Register** a new account → you land on the **disclaimer** → *I understand* → **11-question dosha quiz** → result chart
   → *Start chatting*.
2. Ask **“How should a vata person structure their morning in this season?”** — streamed answer, personalised to the
   dosha and current Ritu, with clickable `[S#]` citations, a context chip (e.g. *Sharad (autumn) · Vata-adjusted*)
   and an expandable *Sources* list.
3. Ask **“Can I take turmeric with warfarin?”** — red **safety banner**: *turmeric ↔ warfarin: Do not take therapeutic-dose
   turmeric with warfarin…* and no answer is generated.
4. Click **New chat** and ask **“Suggest a herb for better sleep”** — the assistant first asks about medication; click
   **No medication — please answer** to get herb suggestions.
5. Open **Profile & Health**, add `warfarin 5 mg` under medications, save. In a new chat ask **“Is turmeric good for joint
   pain?”** — blocked, because the guardrail checks the saved medication list.
6. Open **Dinacharya** → *Generate routine* — a timeline from local sunrise/sunset, season and weather. If the browser
   blocks location, type your city instead (*Change city* works any time).
7. **History** in the chat header reopens earlier conversations.

## Configuration (.env)

All settings live in `.env` at the project root (copy of `.env.example`). The important ones:

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | — | **Required.** Answers + embeddings |
| `GROQ_API_KEY` | — | Fallback LLM when Gemini fails / is overloaded |
| `LLM_PRIMARY_MODEL` | `gemini-3.6-flash` | Main answer model |
| `LLM_CHEAP_MODEL` | `gemini-3.5-flash-lite` | Greetings / JSON checks |
| `LLM_FALLBACK_MODEL` | `openai/gpt-oss-120b` | Groq model |
| `LLM_THINKING_LEVEL` | `minimal` | Gemini 3 thinking before answering (`minimal` ≈ 1.5 s to first token) |
| `GEMINI_EMBEDDING_MODEL` / `EMBEDDING_DIM` | `gemini-embedding-001` / `1024` | Don't change after ingesting |
| `POSTGRES_*`, `DATABASE_URL` | `vedamind` / `127.0.0.1:5432` | Database (keep both in sync) |
| `REDIS_URL` | `redis://127.0.0.1:6379/0` | Cache, rate-limit counters |
| `RAG_SERVICE_URL`, `BACKEND_GUARDRAIL_URL` | `127.0.0.1:8001` / `:8000` | How the two services find each other |
| `RAG_ADMIN_TOKEN` | generated | Shared secret backend ↔ RAG (required; no default in code) |
| `DJANGO_SECRET_KEY`, `JWT_SIGNING_KEY` | generated | Required; production refuses placeholders or values under 32 characters |
| `DEMO_EMAIL` / `DEMO_PASSWORD`, `DEMO_USER_EMAIL` / `DEMO_USER_PASSWORD` | see `.env.example` | Admin and demo accounts (leave empty to create none) |
| `OPEN_METEO_*`, `NOMINATIM_REVERSE_URL`, `GEOCODER_USER_AGENT` | public endpoints | Weather, city search and place names |
| `GUARDRAIL_DIGEST_RECIPIENTS` | empty | Emails for the daily guardrail digest |

Use `127.0.0.1` rather than `localhost` on Windows — `localhost` tries IPv6 first and adds ~2 s to every call.

## Architecture

```
Browser (React, :5173) ──/api──▶ Django backend (:8000) ──▶ PostgreSQL (users, profiles, chats, guardrail rules/audit)
                                   │  auth (JWT + rotating refresh cookie), dosha, dinacharya, weather, guardrails
                                   │  POST /chat ── SSE proxy ──▶ RAG service (FastAPI, :8001)
                                   │                                 1. greeting shortcut / empty-KB check
                                   │                                 2. jailbreak scan
                                   │                                 3. hybrid retrieval (pgvector + full text)
                                   ◀── POST /guardrails/check ─────  4. binding herb-drug check (meds included)
                                                                     5. clarifying question if needed
                                                                     6. Gemini → Groq → Ollama, streamed + cached
Redis: Django cache/throttling, RAG answer cache.  External: Gemini, Groq, Open-Meteo, Nominatim.
```

## Running the tests

```powershell
cd backend;  .\.venv\Scripts\python -m pytest      # 71 tests (needs PostgreSQL running)
cd rag;      .\.venv\Scripts\python -m pytest      # 94 tests (no services needed)
cd frontend; npm test; npm run lint; npm run build # 23 tests
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `...cannot be loaded because running scripts is disabled` | Run scripts as shown: `powershell -ExecutionPolicy Bypass -File scripts\windows\...` |
| `Python 3.12, 3.13 or 3.14 is required` | Install from python.org (tick *Add to PATH*), open a new PowerShell |
| `Port 8000 is already in use` | Another app uses it: `start.ps1 -BackendPort 8010 -RagPort 8011 -FrontendPort 5180` |
| Chat says *“knowledge base has not yet been populated”* | Run `scripts\windows\ingest.ps1` once |
| Ingestion: `GEMINI_API_KEY not configured` / `http 400` | Put a valid key in `.env` (no quotes/spaces) |
| Ingestion is slow / shows *rate limited, waiting* | Normal on the free tier — it retries; takes ~5 min |
| Answers fail: *Could not reach the answer engine* | The RAG service (8001) isn't running — check its window |
| `gemini http 503 … high demand` in the RAG log | Gemini is overloaded; with `GROQ_API_KEY` set it falls back automatically |
| `The pgvector extension is not enabled …` | Run `CREATE EXTENSION vector;` in the `vedamind` DB as the postgres superuser |
| *Location is blocked* on the Dinacharya page | Type your city in the box shown there, or allow location in the browser's site settings and *Retry* |
| Weather card missing | Location not granted yet, or Open-Meteo unreachable |

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | Create account (returns access token, sets refresh cookie) |
| POST | `/api/v1/auth/login` | — | Login |
| POST | `/api/v1/auth/refresh` | refresh cookie | New access token (rotates the cookie) |
| POST | `/api/v1/auth/logout` | refresh cookie | Revoke refresh token |
| GET/PATCH | `/api/v1/users/me` | JWT | Profile (name, timezone, medications, conditions) |
| PATCH | `/api/v1/users/me/medications` | JWT | Replace medication list `{"medications": [...]}` |
| PATCH | `/api/v1/users/me/conditions` | JWT | Replace condition list `{"conditions": [...]}` |
| POST | `/api/v1/users/me/consent` | JWT | Accept disclaimer |
| POST | `/api/v1/users/me/location` | JWT | Save `{"lat", "lon"}` |
| POST | `/api/v1/dosha/assess` | JWT | Submit quiz answers |
| GET | `/api/v1/dosha/profile` | JWT | Dosha profile |
| POST | `/api/v1/chat/` | JWT + consent | Send message → SSE stream |
| GET | `/api/v1/chat/sessions` | JWT | List conversations |
| GET/DELETE | `/api/v1/chat/sessions/{id}` | JWT | Conversation history / delete |
| POST | `/api/v1/guardrails/check` | JWT or RAG token | Herb–drug interaction check |
| GET | `/api/v1/guardrails/interactions/{herb}` | JWT | Known interactions for a herb |
| GET | `/api/v1/weather/current` | JWT | Weather for the saved location |
| GET | `/api/v1/weather/places?q=` | JWT | City search (when browser location is blocked) |
| GET | `/api/v1/dosha/quiz` | JWT | Quiz questions + dosha descriptions |
| GET | `/api/v1/chat/suggestions` | JWT | Starter questions |
| GET | `/api/v1/dinacharya/season` | — | Today's ritu |
| GET | `/api/v1/dinacharya/recommend` | JWT | Generate today's routine |
| GET | `/api/v1/dinacharya/today` | JWT | Today's saved routine |
| GET | `/healthz` | — | DB / Redis / RAG status |

RAG service (internal, `X-RAG-Admin-Token` header): `/api/v1/chat`, `/api/v1/retrieve`, `/api/v1/health`, `/api/v1/ingest`; docs at <http://127.0.0.1:8001/docs>.

## Project structure

```
backend/      Django 5 + DRF: apps/{users, dosha_profiles, conversations, guardrails, interactions_log,
              dinacharya, weather, core}, config/settings/{base,dev,test,prod}, docker/
rag/          FastAPI: app/{core (orchestrator), llm (router + providers), retrieval (pgvector store),
              ingestion (chunk/embed/index CLI), guardrails, prompts, security}, tests/
frontend/     React 18 + Vite + Redux Toolkit: src/{api, components, contexts, hooks, pages, store, utils, tests}
data/raw/     Corpus sources (source.md + metadata.json + rights_manifest.json per source) — see ADDING_DATA.md
scripts/windows/  setup.ps1, infra.ps1, start.ps1, ingest.ps1, stop.ps1
infra/        Production compose template, nginx, monitoring, postgres init
```

`infra/docker-compose.prod.yml` is a production template (nginx/TLS/monitoring); it needs real secrets and a domain
and is not required for local use or the project demo.
