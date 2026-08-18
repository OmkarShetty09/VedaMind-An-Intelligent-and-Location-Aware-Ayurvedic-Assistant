#!/usr/bin/env bash
set -euo pipefail

# Blue-green-ish deploy: pull, build, migrate, reload.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "==> Pulling images and building"
docker compose -f infra/docker-compose.prod.yml build --pull

echo "==> Running migrations"
docker compose -f infra/docker-compose.prod.yml run --rm backend python manage.py migrate --noinput

echo "==> Collecting static files"
docker compose -f infra/docker-compose.prod.yml run --rm backend python manage.py collectstatic --noinput

echo "==> Rolling out"
docker compose -f infra/docker-compose.prod.yml up -d --remove-orphans

echo "==> Health check"
./infra/scripts/wait-for-it.sh http://localhost/healthz 60

echo "Deploy complete."
