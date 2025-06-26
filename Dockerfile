# Dockerfile for Django Portfolio Application

# Use official Python image as base
FROM python:3.11-slim

# Set environment variables for Python
# Don't write .pyc files (reduces image size)
ENV PYTHONDONTWRITEBYTECODE=1

# Force Python to run in unbuffered mode (better for Docker logs)
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for the application
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files
COPY . .

# Copy and make entrypoint script executable
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set the entrypoint script to run before the main command
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command to run the Django application
CMD ["gunicorn", "portfolio_django.wsgi:application", "--bind", "0.0.0.0:8000"]