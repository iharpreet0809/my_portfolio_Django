#!/bin/sh

# Set environment variables for the script
# These should ideally come from your Docker Compose environment,
# but explicitly setting them here ensures the script has access.
# Make sure these match your .env or docker-compose.yml settings.
DB_HOST=$MYSQL_HOST
DB_PORT=$MYSQL_PORT
DB_NAME=$MYSQL_DATABASE
DB_USER=$MYSQL_USER
DB_PASSWORD=$MYSQL_PASSWORD

echo "Waiting for database at $DB_HOST:$DB_PORT..."

# Loop until the database is available
# Using netcat (nc) to check if the port is open
# If nc is not available, you might need to install it in Dockerfile
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done

echo "Database is ready! Applying migrations and collecting static files."

# Run Django migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

echo "Starting Gunicorn server."
# Start the Gunicorn server
exec gunicorn portfolio_django.wsgi:application --bind 0.0.0.0:8000
