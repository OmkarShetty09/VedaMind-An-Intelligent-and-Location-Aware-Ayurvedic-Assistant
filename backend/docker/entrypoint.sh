#!/bin/sh
set -e

echo "Waiting for postgres..."
python - <<'EOF'
import os, sys, time
import psycopg
url = os.environ.get("DATABASE_URL")
conninfo = url or (
    f"host={os.environ.get('POSTGRES_HOST','postgres')} "
    f"port={os.environ.get('POSTGRES_PORT','5432')} "
    f"dbname={os.environ.get('POSTGRES_DB','vedamind')} "
    f"user={os.environ.get('POSTGRES_USER','vedamind')} "
    f"password={os.environ.get('POSTGRES_PASSWORD','vedamind')}"
)
for i in range(60):
    try:
        psycopg.connect(conninfo, connect_timeout=2).close()
        break
    except Exception:
        time.sleep(1)
else:
    sys.exit("postgres not reachable")
EOF

# Only the web process migrates; worker/beat start after it (running migrate in parallel races).
migrate_and_collect() {
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
}

if [ "$1" = "worker" ]; then
    exec celery -A config worker -l info
elif [ "$1" = "beat" ]; then
    exec celery -A config beat -l info --schedule /tmp/celerybeat-schedule
elif [ "$1" = "runserver" ]; then
    # Dev server serves static files itself (DEBUG); collectstatic would only write into the bind mount.
    python manage.py migrate --noinput
    exec python manage.py runserver 0.0.0.0:8000
elif [ -z "$1" ] || [ "$1" = "gunicorn" ]; then
    migrate_and_collect
    if [ "$1" = "gunicorn" ]; then
        exec "$@"
    fi
    exec gunicorn config.wsgi:application -c docker/gunicorn.conf.py
else
    exec "$@"
fi
