# Dockerfile for Django Portfolio Application
# This file defines how to build a Docker image for the Django application

# Use official Python image as base
# Python 3.11-slim provides a good balance of features and image size
FROM python:3.11-slim

# Set environment variables for Python
#Don't write .pyc files (reduces image size)
ENV PYTHONDONTWRITEBYTECODE=1  
# Force Python to run in unbuffered mode (better for Docker logs)
ENV PYTHONUNBUFFERED=1  

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for the application
# These are needed for MySQL client, compilation, and networking tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \  # C compiler for building Python packages
        default-libmysqlclient-dev \  # MySQL development libraries
        pkg-config \  # Package configuration utility
        netcat-traditional && \  # Network utility for health checks
    apt-get clean && \  # Clean up package cache
    rm -rf /var/lib/apt/lists/*  # Remove package lists to reduce image size

# Install Python dependencies first to leverage Docker cache
# This layer will be cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files
# This includes all application code, templates, and static files
COPY . .

# Copy and make entrypoint script executable
# The entrypoint script handles database migrations and other startup tasks
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set the entrypoint script to run before the main command
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command to run the Django application
# Gunicorn is a production-grade WSGI server for Python web applications
CMD ["gunicorn", "portfolio_django.wsgi:application", "--bind", "0.0.0.0:8000"]
