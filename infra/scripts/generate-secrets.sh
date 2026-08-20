#!/usr/bin/env bash
set -euo pipefail

# Generate strong secrets for .env (idempotent - never overwrites existing).
ENV_FILE="$(cd "$(dirname "$0")/../.." && pwd)/.env"

python - <<'PY'
import os, secrets, sys
from pathlib import Path

env_file = Path(sys.argv[1])
write = []
if env_file.exists():
    existing = env_file.read_text()
else:
    existing = ""

def upsert(key, factory):
    if key in existing:
        return
    write.append(f"{key}={factory()}")

upsert("DJANGO_SECRET_KEY", lambda: secrets.token_urlsafe(64))
upsert("JWT_SIGNING_KEY", lambda: secrets.token_urlsafe(48))
upsert("POSTGRES_PASSWORD", lambda: secrets.token_urlsafe(32))
upsert("RAG_ADMIN_TOKEN", lambda: secrets.token_urlsafe(48))
upsert("OPENAI_API_KEY", lambda: "")
upsert("GEMINI_API_KEY", lambda: "")
upsert("GROQ_API_KEY", lambda: "")
upsert("OLLAMA_BASE_URL", lambda: "http://localhost:11434/v1")
upsert("OPENWEATHER_API_KEY", lambda: "")

if write:
    with env_file.open("a") as fh:
        fh.write("\n" + "\n".join(write) + "\n")
    print("Added missing secrets to", env_file)
else:
    print("Secrets already present; nothing changed.")
PY "$ENV_FILE"
