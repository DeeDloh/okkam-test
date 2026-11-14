#!/bin/sh
set -e

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
api_pid=$!

trap 'kill "$api_pid" 2>/dev/null || true' EXIT

alembic upgrade head

export PGPASSWORD="$POSTGRES_PASSWORD"

count=$(psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -At -v ON_ERROR_STOP=1 \
    -c "SELECT COUNT(*) FROM observations")

if [ "$count" -eq 0 ]; then
    psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        -v ON_ERROR_STOP=1 -f /app/init/01_load.sql
else
    echo "Данные уже загружены"
fi

wait "$api_pid"