#!/bin/sh
# Docker Entrypoint Script for Django Portfolio Application
# This script runs before the main application starts to ensure proper setup

set -e  # Exit immediately if a command exits with a non-zero status
# This ensures the container stops if any command fails

# Use environment variables from Docker Compose directly
# Set default values for database connection if not provided
DB_HOST="${MYSQL_HOST:-mysql}"  # Default to 'mysql' service name
DB_PORT="${MYSQL_PORT:-3306}"   # Default to MySQL port 3306

echo "Waiting for database at $DB_HOST:$DB_PORT..."

# Wait until the database port is open
# This ensures Django doesn't start before MySQL is ready
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5  # Wait 0.5 seconds before checking again
done

echo "Database is ready! Running Django setup..."

# Run Django database migrations
# This creates/updates database tables based on models
python manage.py migrate --noinput

# Collect static files
# This gathers all static files (CSS, JS, images) into STATIC_ROOT for Nginx to serve
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
# Run Gunicorn server (pass any CMD from Dockerfile)
# exec replaces the current shell process with the new command
exec "$@"
