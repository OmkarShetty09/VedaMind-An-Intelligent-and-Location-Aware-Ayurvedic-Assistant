#!/usr/bin/env bash
set -euo pipefail

# Copy of infra/scripts/backup.sh kept for the postgres-specific host tools.
BACKUP_DIR="$(cd "$(dirname "$0")/../.." && pwd)/infra/backups"
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
FILE="$BACKUP_DIR/vedamind-$STAMP.sql.gz"

docker compose -f infra/docker-compose.prod.yml exec -T postgres \
  pg_dump -U "${POSTGRES_USER:-vedamind}" "${POSTGRES_DB:-vedamind}" | gzip > "$FILE"
echo "Backup written to $FILE"
echo "$FILE" > "$BACKUP_DIR/.latest"
