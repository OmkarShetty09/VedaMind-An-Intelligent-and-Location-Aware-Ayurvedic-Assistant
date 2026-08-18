#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

docker compose exec -T backend python manage.py migrate --noinput
docker compose exec -T backend python manage.py seed_demo_data
docker compose exec -T backend python manage.py create_superuser
echo "Database seeded."
