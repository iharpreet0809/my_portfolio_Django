#!/bin/bash

echo "🔍 DOCKER VOLUME LOCATION CHECKER"
echo "================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Get project info
PROJECT_NAME=$(basename $(pwd))
print_info "Current Project: $PROJECT_NAME"

echo ""
print_info "DOCKER VOLUMES FOR THIS PROJECT:"
echo "================================"

# List all volumes for this project
docker volume ls | grep "$PROJECT_NAME" || echo "No volumes found for this project"

echo ""
print_info "VOLUME DETAILS:"
echo "==============="

# Check MySQL volume
MYSQL_VOLUME="${PROJECT_NAME}_mysql_data"
if docker volume inspect $MYSQL_VOLUME >/dev/null 2>&1; then
    print_status "MySQL Volume: $MYSQL_VOLUME"
    
    # Show volume location
    VOLUME_PATH=$(docker volume inspect $MYSQL_VOLUME | grep Mountpoint | cut -d'"' -f4)
    echo "   Location: $VOLUME_PATH"
    
    # Show size
    echo "   Size: $(docker run --rm -v $MYSQL_VOLUME:/data alpine du -sh /data 2>/dev/null | cut -f1)"
    
    # Show contents
    echo "   Contents:"
    docker run --rm -v $MYSQL_VOLUME:/data alpine ls -la /data | head -10
else
    print_warning "MySQL volume not found: $MYSQL_VOLUME"
fi

echo ""

# Check Redis volume
REDIS_VOLUME="${PROJECT_NAME}_redis_data"
if docker volume inspect $REDIS_VOLUME >/dev/null 2>&1; then
    print_status "Redis Volume: $REDIS_VOLUME"
    
    # Show volume location
    VOLUME_PATH=$(docker volume inspect $REDIS_VOLUME | grep Mountpoint | cut -d'"' -f4)
    echo "   Location: $VOLUME_PATH"
    
    # Show size
    echo "   Size: $(docker run --rm -v $REDIS_VOLUME:/data alpine du -sh /data 2>/dev/null | cut -f1)"
    
    # Show contents
    echo "   Contents:"
    docker run --rm -v $REDIS_VOLUME:/data alpine ls -la /data | head -5
else
    print_warning "Redis volume not found: $REDIS_VOLUME"
fi

echo ""
print_info "ALL DOCKER VOLUMES ON SYSTEM:"
echo "============================="
docker volume ls

echo ""
print_info "VOLUME STORAGE EXPLANATION:"
echo "=========================="
echo "• Docker volumes are stored in Docker's internal directory"
echo "• On Linux: /var/lib/docker/volumes/{volume_name}/_data/"
echo "• On Windows: Inside WSL2 virtual disk (not directly accessible)"
echo "• Volumes are NOT visible in your project directory"
echo "• Use 'docker run' commands to access volume contents"

echo ""
print_info "TO ACCESS MYSQL DATA:"
echo "===================="
echo "# Enter MySQL container:"
echo "docker compose exec mysql bash"
echo ""
echo "# Or run MySQL commands:"
echo "docker compose exec mysql mysql -uroot -p\${MYSQL_ROOT_PASSWORD}"
echo ""
echo "# Or backup data:"
echo "docker compose exec mysql mysqldump -uroot -p\${MYSQL_ROOT_PASSWORD} --all-databases > backup.sql"

echo ""
print_info "TO ACCESS VOLUME FILES DIRECTLY:"
echo "==============================="
echo "# Mount volume to temporary container:"
echo "docker run --rm -it -v ${PROJECT_NAME}_mysql_data:/data alpine sh"
echo "# Then inside container: ls -la /data"