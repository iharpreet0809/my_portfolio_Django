echo "🚀 Entrypoint script is executing..."

#!/bin/sh
# This script runs before the main application starts to ensure proper setup
# Entrypoint script for Django application with MySQL

set -e  # Exit on any error
# Use environment variables from Docker Compose directly
# Set default values for database connection if not provided
DB_HOST="${MYSQL_HOST:-mysql}"
DB_PORT="${MYSQL_PORT:-3306}"

echo "⏳ Waiting for MySQL at $DB_HOST:$DB_PORT..."
# Wait until the database port is open
# This ensures Django doesn't start before MySQL is ready
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5
done
echo "✅ MySQL Database is up and running django setup!"

echo "🧱 Checking for pending migrations..."
python manage.py makemigrations --check --dry-run > /dev/null 2>&1 || {
    echo "🔧 Making new migrations..."
    python manage.py makemigrations
}

echo "🚀 Applying migrations..."
python manage.py migrate --noinput

echo "Migrations applied with migrate!"

# This gathers all static files (CSS, JS, images) into STATIC_ROOT for Nginx to serve
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🟢 Starting Gunicorn server..."
# exec replaces the current shell process with the new command
exec "$@"