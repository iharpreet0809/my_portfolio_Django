#!/bin/bash

echo "🚀 SIMPLE PORTFOLIO BACKUP & RESTORE"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to backup essential data only
backup_essential_data() {
    echo ""
    print_info "BACKING UP ESSENTIAL DATA ONLY"
    echo "==============================="
    
    # Create backup directory in /home/ubuntu/data_backups
    BACKUP_BASE_DIR="/home/ubuntu/data_backups"
    BACKUP_DIR="$BACKUP_BASE_DIR/mysql_migration_$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    print_warning "Backup location: $BACKUP_DIR"
    
    # Check if containers are running
    if ! docker compose ps | grep -q "mysql.*Up"; then
        print_error "MySQL container is not running!"
        echo "Please start containers first: docker compose up -d"
        return 1
    fi
    
    # 1. Backup MySQL database (SQL dump)
    print_warning "Creating MySQL database backup..."
    docker compose exec mysql mysqldump -uroot -p${MYSQL_ROOT_PASSWORD} --all-databases > $BACKUP_DIR/mysql_backup.sql
    
    if [ $? -eq 0 ]; then
        print_status "MySQL backup created: mysql_backup.sql"
    else
        print_error "MySQL backup failed!"
        return 1
    fi
    
    # 2. Backup MySQL volume data
    print_warning "Creating MySQL volume backup..."
    PROJECT_NAME=$(basename $(pwd))
    MYSQL_VOLUME="${PROJECT_NAME}_mysql_data"
    
    docker compose stop mysql
    docker run --rm -v $MYSQL_VOLUME:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/mysql_volume.tar.gz -C /data .
    docker compose start mysql
    
    print_status "MySQL volume backup created: mysql_volume.tar.gz"
    
    # 3. Backup Redis data
    print_warning "Creating Redis backup..."
    REDIS_VOLUME="${PROJECT_NAME}_redis_data"
    
    docker compose stop redis
    docker run --rm -v $REDIS_VOLUME:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
    docker compose start redis
    
    print_status "Redis backup created: redis_data.tar.gz"
    
    # 4. Backup .env file
    print_warning "Backing up .env file..."
    cp .env $BACKUP_DIR/
    print_status ".env file backed up"
    
    # 5. Backup SSL certificates (if exists)
    if [ -d "certbot" ]; then
        print_warning "Backing up SSL certificates..."
        cp -r certbot $BACKUP_DIR/
        print_status "SSL certificates backed up"
    else
        print_warning "No SSL certificates found, skipping..."
    fi
    
    # 6. Backup nginx config (if exists)
    if [ -d "nginx" ]; then
        print_warning "Backing up nginx config..."
        cp -r nginx $BACKUP_DIR/
        print_status "Nginx config backed up"
    else
        print_warning "No nginx config found, skipping..."
    fi
    
    # Stop all containers for safe migration
    print_warning "Stopping all containers for safe migration..."
    docker compose down
    
    print_status "BACKUP COMPLETED!"
    echo ""
    print_info "Backup saved to: $BACKUP_DIR"
    print_info "Contents:"
    ls -la $BACKUP_DIR/
    
    echo ""
    print_info "NEXT STEPS:"
    echo "1. Clone fresh project code"
    echo "2. Copy this script to new project"
    echo "3. Run: ./simple_backup_restore.sh restore $BACKUP_DIR"
}

# Function to restore from backup
restore_from_backup() {
    BACKUP_DIR=$1
    
    if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
        print_error "Backup directory not provided or not found!"
        echo "Usage: ./simple_backup_restore.sh restore /home/ubuntu/data_backups/mysql_migration_YYYYMMDD_HHMMSS"
        return 1
    fi
    
    print_warning "Restoring from backup: $BACKUP_DIR"
    
    # Stop containers
    docker compose down
    
    # Get project info
    PROJECT_NAME=$(basename $(pwd))
    MYSQL_VOLUME="${PROJECT_NAME}_mysql_data"
    REDIS_VOLUME="${PROJECT_NAME}_redis_data"
    
    # 1. Restore .env file
    if [ -f "$BACKUP_DIR/.env" ]; then
        print_warning "Restoring .env file..."
        cp $BACKUP_DIR/.env .
        print_status ".env file restored"
    fi
    
    # 2. Restore SSL certificates
    if [ -d "$BACKUP_DIR/certbot" ]; then
        print_warning "Restoring SSL certificates..."
        cp -r $BACKUP_DIR/certbot .
        print_status "SSL certificates restored"
    fi
    
    # 3. Restore nginx config
    if [ -d "$BACKUP_DIR/nginx" ]; then
        print_warning "Restoring nginx config..."
        cp -r $BACKUP_DIR/nginx .
        print_status "Nginx config restored"
    fi
    
    # 4. Restore MySQL volume
    if [ -f "$BACKUP_DIR/mysql_volume.tar.gz" ]; then
        print_warning "Restoring MySQL volume..."
        
        # Remove existing volume
        docker volume rm $MYSQL_VOLUME 2>/dev/null || echo "Volume not found"
        
        # Create new volume
        docker volume create $MYSQL_VOLUME
        
        # Restore data
        docker run --rm -v $MYSQL_VOLUME:/data -v $BACKUP_DIR:/backup alpine tar xzf /backup/mysql_volume.tar.gz -C /data
        
        print_status "MySQL volume restored"
    fi
    
    # 5. Restore Redis volume
    if [ -f "$BACKUP_DIR/redis_data.tar.gz" ]; then
        print_warning "Restoring Redis data..."
        
        # Remove existing volume
        docker volume rm $REDIS_VOLUME 2>/dev/null || echo "Volume not found"
        
        # Create new volume
        docker volume create $REDIS_VOLUME
        
        # Restore data
        docker run --rm -v $REDIS_VOLUME:/data -v $BACKUP_DIR:/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
        
        print_status "Redis data restored"
    fi
    
    # 6. Build and start containers
    print_warning "Building and starting containers..."
    docker compose up --build -d
    
    # Wait for services
    print_warning "Waiting for services to start..."
    sleep 45
    
    print_status "RESTORE COMPLETED!"
    
    # Check status
    echo ""
    print_info "Checking service status..."
    docker compose ps
}

# Main script logic
case "$1" in
    "backup")
        backup_essential_data
        ;;
    "restore")
        restore_from_backup $2
        ;;
    *)
        echo "Usage: $0 {backup|restore}"
        echo ""
        echo "Commands:"
        echo "  backup                     - Backup essential data (MySQL, Redis, SSL, .env)"
        echo "  restore BACKUP_DIR         - Restore from backup directory"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 restore /home/ubuntu/data_backups/mysql_migration_20241027_123456"
        ;;
esac