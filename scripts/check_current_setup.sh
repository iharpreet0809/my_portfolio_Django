#!/bin/bash

echo "🔍 CHECKING CURRENT DOCKER SETUP"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Get project information
PROJECT_DIR=$(pwd)
PROJECT_NAME=$(basename "$PROJECT_DIR")

print_info "Project Directory: $PROJECT_DIR"
print_info "Project Name: $PROJECT_NAME"

echo ""
print_info "DOCKER COMPOSE SERVICES:"
echo "========================"
docker compose ps 2>/dev/null || echo "Docker Compose not running"

echo ""
print_info "DOCKER VOLUMES:"
echo "==============="
docker volume ls | grep "$PROJECT_NAME" || echo "No project volumes found"

echo ""
print_info "EXPECTED VOLUMES FOR YOUR PROJECT:"
echo "=================================="
echo "• ${PROJECT_NAME}_mysql_data"
echo "• ${PROJECT_NAME}_redis_data"

echo ""
print_info "CHECKING VOLUME CONTENTS:"
echo "========================="

# Check MySQL volume
MYSQL_VOLUME="${PROJECT_NAME}_mysql_data"
if docker volume inspect $MYSQL_VOLUME >/dev/null 2>&1; then
    print_status "MySQL volume exists: $MYSQL_VOLUME"
    echo "MySQL data size:"
    docker run --rm -v $MYSQL_VOLUME:/data alpine du -sh /data 2>/dev/null || echo "Cannot check size"
else
    print_warning "MySQL volume not found: $MYSQL_VOLUME"
fi

# Check Redis volume
REDIS_VOLUME="${PROJECT_NAME}_redis_data"
if docker volume inspect $REDIS_VOLUME >/dev/null 2>&1; then
    print_status "Redis volume exists: $REDIS_VOLUME"
    echo "Redis data size:"
    docker run --rm -v $REDIS_VOLUME:/data alpine du -sh /data 2>/dev/null || echo "Cannot check size"
else
    print_warning "Redis volume not found: $REDIS_VOLUME"
fi

echo ""
print_info "IMPORTANT FILES TO BACKUP:"
echo "=========================="
[ -f ".env" ] && print_status ".env file exists" || print_warning ".env file missing"
[ -d "staticfiles" ] && print_status "staticfiles directory exists" || print_warning "staticfiles directory missing"
[ -d "mediafiles" ] && print_status "mediafiles directory exists" || print_warning "mediafiles directory missing"
[ -d "logs" ] && print_status "logs directory exists" || print_warning "logs directory missing"
[ -d "certbot" ] && print_status "certbot directory exists" || print_warning "certbot directory missing"
[ -d "nginx" ] && print_status "nginx directory exists" || print_warning "nginx directory missing"

echo ""
print_info "BACKUP SCRIPT COMPATIBILITY:"
echo "============================"
if [ -f "backup_restore_database.sh" ]; then
    print_status "Backup script exists and is configured for:"
    echo "• MySQL Volume: $MYSQL_VOLUME"
    echo "• Redis Volume: $REDIS_VOLUME"
    echo "• Project: $PROJECT_NAME"
else
    print_warning "Backup script not found"
fi

echo ""
print_info "RECOMMENDED BACKUP COMMAND:"
echo "=========================="
echo "./backup_restore_database.sh migrate"

echo ""
print_info "CURRENT ENVIRONMENT:"
echo "==================="
if [ -f ".env" ]; then
    echo "DEBUG=$(grep DEBUG .env 2>/dev/null || echo 'Not set')"
    echo "MYSQL_DATABASE=$(grep MYSQL_DATABASE .env 2>/dev/null || echo 'Not set')"
    echo "REDIS_URL=$(grep REDIS_URL .env 2>/dev/null || echo 'Not set')"
else
    print_warning "No .env file found"
fi