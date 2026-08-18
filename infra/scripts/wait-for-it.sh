#!/usr/bin/env bash
set -euo pipefail

# Poll an HTTP endpoint until 200 or timeout. Usage: wait-for-it.sh <url> <seconds>
URL="${1:?url required}"
TIMEOUT="${2:-60}"
I=0
while ! curl -fsS "$URL" >/dev/null 2>&1; do
  I=$((I + 1))
  if [[ "$I" -ge "$TIMEOUT" ]]; then
    echo "Timed out waiting for $URL" >&2
    exit 1
  fi
  sleep 1
done
echo "Ready: $URL"
