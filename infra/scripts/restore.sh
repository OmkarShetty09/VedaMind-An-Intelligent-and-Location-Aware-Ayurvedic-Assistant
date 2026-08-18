#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="$(cd "$(dirname "$0")/../.." && pwd)/infra/backups"
FILE="${1:-$(cat "$BACKUP_DIR/.latest" 2>/dev/null || echo '')}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "Usage: $0 <backup.sql.gz|backup.sql>" >&2
  exit 1
fi

if [[ "$FILE" == *.gz ]]; then
  gunzip -c "$FILE" | docker compose -f infra/docker-compose.prod.yml exec -T postgres \
    psql -U "${POSTGRES_USER:-vedamind}" "${POSTGRES_DB:-vedamind}"
else
  docker compose -f infra/docker-compose.prod.yml exec -T postgres \
    psql -U "${POSTGRES_USER:-vedamind}" "${POSTGRES_DB:-vedamind}" < "$FILE"
fi

echo "Restored from $FILE"
