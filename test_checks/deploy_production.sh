#!/bin/bash

echo "🚀 PRODUCTION DEPLOYMENT SCRIPT"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Please create .env file from .env.production template"
    exit 1
fi

# Check if DEBUG=False in .env
if grep -q "DEBUG=True" .env; then
    print_error "DEBUG is still True in .env file!"
    echo "Please set DEBUG=False for production"
    exit 1
fi

print_status "Environment check passed"

# Stop existing containers
print_warning "Stopping existing containers..."
docker-compose down

# Clean up old images and containers
print_warning "Cleaning up old Docker resources..."
docker system prune -f
docker volume prune -f

# Build and start services
print_status "Building and starting services..."
docker-compose up --build -d

# Wait for services to start
print_warning "Waiting for services to initialize..."
sleep 30

# Check service status
print_status "Checking service status..."
docker-compose ps

# Check logs for any errors
print_status "Checking recent logs..."
docker-compose logs --tail=20

# Test Redis connection
print_status "Testing Redis connection..."
docker-compose exec redis redis-cli ping

# Test Celery worker
print_status "Testing Celery worker..."
docker-compose exec celery celery -A portfolio_django inspect ping

print_status "Deployment completed!"
echo ""
echo "🌐 Your application should be running on:"
echo "   • Web: http://your-domain:8000"
echo "   • Redis: localhost:6379"
echo ""
echo "📊 Monitor services with:"
echo "   • docker-compose logs -f"
echo "   • docker-compose ps"
echo ""
echo "🔧 Useful commands:"
echo "   • Restart: docker-compose restart"
echo "   • Stop: docker-compose down"
echo "   • View logs: docker-compose logs [service-name]"