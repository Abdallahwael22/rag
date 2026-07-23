#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/models/db_schemes/minirag/
alembic upgrade head

echo "Migrations complete. Handing over to CMD..."
cd /app

# Exec replaces the shell process with whatever command was passed via Dockerfile CMD
exec "$@"