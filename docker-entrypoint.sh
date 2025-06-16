#!/bin/sh

set -e  # Exit immediately if a command exits with a non-zero status

# Use environment variables from Docker Compose directly
DB_HOST="${MYSQL_HOST:-mysql}"
DB_PORT="${MYSQL_PORT:-3306}"

echo "Waiting for database at $DB_HOST:$DB_PORT..."

# Wait until the database port is open
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5
done

echo "Database is ready! Running Django setup..."

# Run Django database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
# Run Gunicorn server (pass any CMD from Dockerfile)
exec "$@"
