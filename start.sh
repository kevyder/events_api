#!/bin/bash
set -e

PORT="${PORT:-8080}"
UVICORN_RELOAD="${UVICORN_RELOAD:-false}"

echo "Running database migrations..."
alembic upgrade head

echo "Starting the application on port ${PORT}..."

if [ "${UVICORN_RELOAD}" = "true" ]; then
    exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT}" --reload
fi

exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT}"
