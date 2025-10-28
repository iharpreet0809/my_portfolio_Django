#!/bin/bash

echo "🗄️  DATABASE BACKUP & RESTORE SCRIPT"
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

# Function to backup database
backup_database() {
    echo ""
    print_info "BACKUP DATABASE FUNCTION"
    echo "========================"
    
    # Check if containers are running
    if ! docker compose ps | grep -q "mysql.*Up"; then
        print_error "MySQL container is not running!"
        echo "Please start containers first: docker compose up -d"
        return 1
    fi
    
    # Create backup directory
    BACKUP_DIR="./database_backups"
    mkdir -p $BACKUP_DIR
    
    # Generate backup filename with timestamp
    BACKUP_FILE="$BACKUP_DIR/mysql_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    print_warning "Creating database backup..."
    
    # Create SQL dump
    docker compose exec mysql mysqldump -uroot -p${MYSQL_ROOT_PASSWORD} --all-databases > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        print_status "Database backup created: $BACKUP_FILE"
        
        # Also backup Docker volume data
        print_warning "Creating Docker volume backup..."
        VOLUME_BACKUP="$BACKUP_DIR/mysql_volume_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        
        # Stop MySQL container temporarily
        docker compose stop mysql
        
        # Get the correct project name for volume
        PROJECT_NAME=$(basename $(pwd))
        MYSQL_VOLUME="${PROJECT_NAME}_mysql_data"
        
        # Create volume backup
        docker run --rm -v $MYSQL_VOLUME:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/mysql_volume_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
        
        # Start MySQL container again
        docker compose start mysql
        
        print_status "Volume backup created: $VOLUME_BACKUP"
        
        # Also backup Redis data
        print_warning "Creating Redis backup..."
        REDIS_VOLUME="${PROJECT_NAME}_redis_data"
        REDIS_BACKUP="$BACKUP_DIR/redis_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        
        # Stop Redis container temporarily
        docker compose stop redis
        
        # Create Redis backup
        docker run --rm -v $REDIS_VOLUME:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/redis_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
        
        # Start Redis container again
        docker compose start redis
        
        print_status "Redis backup created: $REDIS_BACKUP"
        
        # List all backups
        echo ""
        print_info "Available backups:"
        ls -la $BACKUP_DIR/
        
    else
        print_error "Database backup failed!"
        return 1
    fi
}

# Function to restore database
restore_database() {
    echo ""
    print_info "RESTORE DATABASE FUNCTION"
    echo "========================="
    
    BACKUP_DIR="./database_backups"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_error "Backup directory not found: $BACKUP_DIR"
        return 1
    fi
    
    # List available backups
    echo "Available SQL backups:"
    ls -la $BACKUP_DIR/*.sql 2>/dev/null || echo "No SQL backups found"
    
    echo ""
    echo "Available volume backups:"
    ls -la $BACKUP_DIR/*.tar.gz 2>/dev/null || echo "No volume backups found"
    
    echo ""
    read -p "Enter backup file path (SQL or volume .tar.gz): " BACKUP_FILE
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        return 1
    fi
    
    # Check if it's SQL or volume backup
    if [[ "$BACKUP_FILE" == *.sql ]]; then
        print_warning "Restoring from SQL backup..."
        
        # Make sure MySQL is running
        docker compose up -d mysql
        sleep 10
        
        # Restore SQL backup
        docker compose exec -T mysql mysql -uroot -p${MYSQL_ROOT_PASSWORD} < $BACKUP_FILE
        
        if [ $? -eq 0 ]; then
            print_status "SQL backup restored successfully!"
        else
            print_error "SQL backup restore failed!"
        fi
        
    elif [[ "$BACKUP_FILE" == *.tar.gz ]]; then
        print_warning "Restoring from volume backup..."
        
        # Stop MySQL container
        docker compose stop mysql
        
        # Get the correct project name for volume
        PROJECT_NAME=$(basename $(pwd))
        MYSQL_VOLUME="${PROJECT_NAME}_mysql_data"
        
        # Remove existing volume
        docker volume rm $MYSQL_VOLUME 2>/dev/null || echo "Volume not found"
        
        # Create new volume
        docker volume create $MYSQL_VOLUME
        
        # Restore volume data
        docker run --rm -v $MYSQL_VOLUME:/data -v $(pwd):/backup alpine tar xzf /backup/$BACKUP_FILE -C /data
        
        # Start MySQL container
        docker compose start mysql
        
        print_status "Volume backup restored successfully!"
        
    else
        print_error "Invalid backup file format. Use .sql or .tar.gz files only."
        return 1
    fi
}

# Function to migrate database safely
migrate_database() {
    echo ""
    print_info "SAFE DATABASE MIGRATION"
    echo "======================="
    
    print_warning "This will:"
    echo "1. Backup current database"
    echo "2. Stop containers"
    echo "3. Move database volume safely"
    echo "4. Allow you to clone new project"
    echo "5. Restore database after cloning"
    
    read -p "Continue? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "Migration cancelled."
        return 0
    fi
    
    # Step 1: Backup
    backup_database
    
    # Step 2: Stop containers
    print_warning "Stopping all containers..."
    docker compose down
    
    # Step 3: Export volume to safe location
    SAFE_BACKUP_DIR="/home/ubuntu/data_backups/mysql_migration_$(date +%Y%m%d_%H%M%S)"
    mkdir -p $SAFE_BACKUP_DIR
    
    print_warning "Exporting MySQL volume to safe location..."
    PROJECT_NAME=$(basename $(pwd))
    MYSQL_VOLUME="${PROJECT_NAME}_mysql_data"
    docker run --rm -v $MYSQL_VOLUME:/data -v $SAFE_BACKUP_DIR:/backup alpine cp -r /data/. /backup/
    
    print_status "Database exported to: $SAFE_BACKUP_DIR"
    
    echo ""
    print_info "NEXT STEPS:"
    echo "1. Clone your new project code"
    echo "2. Copy this script to new project directory"
    echo "3. Run: ./backup_restore_database.sh restore-from-migration $SAFE_BACKUP_DIR"
    echo ""
    print_warning "Safe backup location: $SAFE_BACKUP_DIR"
}

# Function to restore from migration
restore_from_migration() {
    MIGRATION_DIR=$1
    
    if [ -z "$MIGRATION_DIR" ] || [ ! -d "$MIGRATION_DIR" ]; then
        print_error "Migration directory not provided or not found!"
        echo "Usage: ./backup_restore_database.sh restore-from-migration /path/to/migration/dir"
        return 1
    fi
    
    print_warning "Restoring database from migration..."
    
    # Stop containers
    docker compose down
    
    # Get the correct project name for volume
    PROJECT_NAME=$(basename $(pwd))
    MYSQL_VOLUME="${PROJECT_NAME}_mysql_data"
    
    # Remove existing volume
    docker volume rm $MYSQL_VOLUME 2>/dev/null || echo "Volume not found"
    
    # Create new volume
    docker volume create $MYSQL_VOLUME
    
    # Restore data
    docker run --rm -v $MYSQL_VOLUME:/data -v $MIGRATION_DIR:/backup alpine cp -r /backup/. /data/
    
    # Start containers
    docker compose up -d
    
    print_status "Database restored from migration!"
    print_info "You can now remove the migration directory: $MIGRATION_DIR"
}

# Main script logic
case "$1" in
    "backup")
        backup_database
        ;;
    "restore")
        restore_database
        ;;
    "migrate")
        migrate_database
        ;;
    "restore-from-migration")
        restore_from_migration $2
        ;;
    *)
        echo "Usage: $0 {backup|restore|migrate|restore-from-migration}"
        echo ""
        echo "Commands:"
        echo "  backup                     - Create database backup"
        echo "  restore                    - Restore from existing backup"
        echo "  migrate                    - Safely migrate database before cloning new project"
        echo "  restore-from-migration DIR - Restore database after cloning new project"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 migrate"
        echo "  $0 restore-from-migration /tmp/mysql_migration_20241027_123456"
        ;;
esac