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

# Copy and make entrypoint script executable for the container
#now we are in the container and running the script wirh entrypoint.sh
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

#entrypoint.sh make it executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set the entrypoint script to run before the main command
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]


# Default command to run the Django application
# Yes, this CMD command runs inside the container. It starts Gunicorn (Python WSGI server)
# binding it to all network interfaces (0.0.0.0) on port 8000
CMD ["gunicorn", "portfolio_django.wsgi:application", "--bind", "0.0.0.0:8000"]