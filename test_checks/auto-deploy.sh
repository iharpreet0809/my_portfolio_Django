#!/bin/bash

echo "🚀 AUTO-DEPLOYMENT SCRIPT"
echo "========================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Change to project directory
cd /home/ubuntu/githubs/live_portfolio

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Not in project directory!"
    exit 1
fi

print_status "Starting deployment..."

# Pull latest changes
print_warning "Pulling latest code..."
git pull origin main

if [ $? -ne 0 ]; then
    print_error "Git pull failed!"
    exit 1
fi

print_status "Code updated successfully"

# Check for changes in requirements or Docker files
if git diff HEAD~1 --name-only | grep -E "(requirements.txt|Dockerfile|docker-compose.yml)"; then
    print_warning "Dependencies changed, rebuilding containers..."
    docker compose down
    docker compose up --build -d
else
    print_warning "Restarting application containers..."
    docker compose restart django celery celery-beat
fi

# Wait for services to start
print_warning "Waiting for services to start..."
sleep 30

# Check service health
print_status "Checking service health..."
docker compose ps

# Check if Django is responding
if curl -f -s http://localhost:8000 > /dev/null; then
    print_status "Django is responding"
else
    print_error "Django is not responding!"
fi

# Check Celery worker
if docker compose exec celery celery -A portfolio_django inspect ping > /dev/null 2>&1; then
    print_status "Celery worker is healthy"
else
    print_error "Celery worker is not responding!"
fi

print_status "Deployment completed!"
echo ""
echo "🌐 Website: https://iharpreet.com"
echo "📊 Monitor: docker compose ps"
echo "📋 Logs: docker compose logs -f"