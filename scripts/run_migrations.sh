#!/bin/bash
# Run database migrations for V1

set -e

DB_HOST="${POSTGRES_HOST:-127.0.0.1}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-omni_csx}"
DB_USER="${POSTGRES_USER:-omni}"
DB_PASSWORD="${POSTGRES_PASSWORD:-omni}"

MIGRATIONS_DIR="$(dirname "$0")/../migrations"

echo "Running database migrations..."
echo "Database: $DB_NAME at $DB_HOST:$DB_PORT"

export PGPASSWORD="$DB_PASSWORD"

for migration in $(ls -1 "$MIGRATIONS_DIR"/*.sql | sort); do
    echo "Executing: $(basename "$migration")"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration"
done

echo "Migrations completed!"

psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt"