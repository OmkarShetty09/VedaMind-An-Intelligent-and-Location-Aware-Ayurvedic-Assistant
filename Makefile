.PHONY: setup dev dev-backend dev-frontend dev-rag migrate seed-db seed-corpus test test-backend test-rag test-frontend lint format eval build up down logs backup restore deploy secrets

# ---- bootstrap ----
setup:
	cp -n .env.example .env || true
	docker compose up -d postgres redis
	make migrate seed-db

# ---- dev (all services, live reload) ----
dev:
	docker compose up --build

dev-backend:
	docker compose up --build backend

dev-frontend:
	docker compose up --build frontend

dev-rag:
	docker compose up --build rag

# ---- database ----
migrate:
	docker compose exec backend python manage.py migrate

seed-db:
	docker compose exec backend python manage.py seed_demo_data
	docker compose exec backend python manage.py create_superuser

seed-corpus:
	bash infra/scripts/seed-rag-corpus.sh

# ---- tests ----
test: test-backend test-rag test-frontend

test-backend:
	docker compose exec backend pytest

test-rag:
	docker compose exec rag pytest

test-frontend:
	cd frontend && npm test

# ---- quality ----
lint:
	docker compose exec backend ruff check .
	docker compose exec rag ruff check .
	cd frontend && npm run lint

format:
	docker compose exec backend ruff format .
	docker compose exec rag ruff format .

# ---- evals ----
eval:
	docker compose exec rag python -m app.evaluation.scripts.eval_retrieval
	docker compose exec rag python -m app.evaluation.scripts.eval_guardrails

# ---- build / lifecycle ----
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

# ---- ops ----
backup:
	bash infra/scripts/backup.sh

restore:
	bash infra/scripts/restore.sh

deploy:
	bash infra/scripts/deploy.sh

secrets:
	bash infra/scripts/generate-secrets.sh