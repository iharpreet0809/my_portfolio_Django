#!/bin/bash

echo "🔧 FIXING MYSQL PERMISSION ISSUE"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Stop all containers
print_warning "Stopping all containers..."
docker compose down

# Remove MySQL volume (this will delete existing data - make sure you have backup)
print_warning "Removing MySQL volume to fix permissions..."
docker volume rm live_portfolio_mysql_data 2>/dev/null || echo "Volume not found, continuing..."

# Clean up Docker system
print_warning "Cleaning up Docker system..."
docker system prune -f

# Remove any orphaned containers
print_warning "Removing any orphaned containers..."
docker container prune -f

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Please create .env file with your production settings"
    exit 1
fi

# Check if DEBUG=False
if grep -q "DEBUG=True" .env; then
    print_error "DEBUG is still True in .env file!"
    echo "Please set DEBUG=False for production"
    exit 1
fi

print_status "Environment check passed"

# Build and start services
print_status "Building and starting services with fixed MySQL configuration..."
docker compose up --build -d

# Wait for services to start
print_warning "Waiting for services to initialize..."
sleep 45

# Check service status
print_status "Checking service status..."
docker compose ps

# Check MySQL logs
print_status "Checking MySQL logs..."
docker logs mysql --tail=10

# Check if MySQL is healthy
print_status "Checking MySQL health..."
docker compose exec mysql mysqladmin ping -uroot -p${MYSQL_ROOT_PASSWORD} 2>/dev/null && echo "MySQL is healthy!" || echo "MySQL still starting..."

print_status "Deployment completed!"
echo ""
echo "🌐 Your application should be running on:"
echo "   • Web: http://your-domain:8000"
echo "   • Redis: localhost:6379"
echo ""
echo "📊 Monitor services with:"
echo "   • docker compose logs -f"
echo "   • docker compose ps"