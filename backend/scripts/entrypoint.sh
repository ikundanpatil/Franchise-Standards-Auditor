#!/usr/bin/env bash
# Container entrypoint.
#   RUN_MIGRATIONS=1  -> `alembic upgrade head` before starting
#   SEED_ON_START=1   -> `python -m app.db.seed` before starting (idempotent)
set -euo pipefail

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  echo "[entrypoint] running database migrations..."
  alembic upgrade head
fi

if [ "${SEED_ON_START:-0}" = "1" ]; then
  echo "[entrypoint] seeding database..."
  python -m app.db.seed || echo "[entrypoint] seed skipped/failed (continuing)"
fi

echo "[entrypoint] starting: $*"
exec "$@"
