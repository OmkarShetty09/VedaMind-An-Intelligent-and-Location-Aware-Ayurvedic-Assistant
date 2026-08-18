#!/usr/bin/env bash
set -euo pipefail

# pg_dump of the application database to infra/backups.
BACKUP_DIR="$(cd "$(dirname "$0")/../.." && pwd)/infra/backups"
mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d-%H%M%S)"
FILE="$BACKUP_DIR/vedamind-$STAMP.sql"

docker compose -f infra/docker-compose.prod.yml exec -T postgres \
  pg_dump -U "${POSTGRES_USER:-vedamind}" "${POSTGRES_DB:-vedamind}" > "$FILE"

echo "Backup written to $FILE"
echo "$FILE" > "$BACKUP_DIR/.latest"
