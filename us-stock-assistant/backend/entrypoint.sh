#!/bin/bash
set -e

# Railway provides DATABASE_URL, skip pg_isready check
echo "Starting deployment process..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
exec "$@"
