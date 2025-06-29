#!/bin/sh
# 🚀 Entrypoint script for Django with MySQL
# Ensures DB is ready, applies migrations, collects static files

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Entrypoint script is executing..."

# Set default DB host and port if not provided
DB_HOST="${MYSQL_HOST:-mysql}"
DB_PORT="${MYSQL_PORT:-3306}"

echo "⏳ Waiting for MySQL at $DB_HOST:$DB_PORT..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 0.5
done
echo "✅ MySQL is available!"

# Run Django setup tasks
echo "🧱 Checking for pending migrations..."
if ! python manage.py makemigrations --check --dry-run > /dev/null 2>&1; then
    echo "🔧 Making new migrations..."
    python manage.py makemigrations
else
    echo "✅ No new migrations needed."
fi

echo "🚀 Applying migrations..."
python manage.py migrate --noinput
echo "✅ Migrations completed."

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected."

echo "🟢 Starting application: $*"
exec "$@"
