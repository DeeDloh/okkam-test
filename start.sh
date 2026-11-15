#!/bin/sh
set -eu

DB_HOST="${POSTGRES_HOST:-db}"
export PGPASSWORD="$POSTGRES_PASSWORD"

run_psql() {
    psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        -v ON_ERROR_STOP=1 "$@"
}

echo "миграция"
alembic upgrade head

count=$(run_psql -At -c "SELECT COUNT(*) FROM observations")

if [ "$count" -eq 0 ]; then
    echo "Загрузка данных data.csv"
    run_psql -f /app/init/01_load.sql
    echo "Данные загружены"
else
    echo "Данные уже загружены ($count строк)"
fi

echo "Запуск API"
exec uvicorn app.main:app --host 0.0.0.0 --port 80
