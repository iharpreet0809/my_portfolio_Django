# Production Deployment Guide with Database Migration

## 🗄️ Safe Database Migration Process

### When you need to clone fresh project code but keep existing database:

## Method 1: Complete Migration (Recommended)

### Step 1: Backup Current Database
```bash
# In your current project directory
chmod +x backup_restore_database.sh
./backup_restore_database.sh migrate
```

This will:
- ✅ Create SQL backup
- ✅ Create volume backup  
- ✅ Export database to safe temp location
- ✅ Stop containers
- ✅ Give you safe backup path

### Step 2: Clone Fresh Project
```bash
# Move to parent directory
cd ..

# Rename old project (as backup)
mv live_portfolio live_portfolio_backup_$(date +%Y%m%d)

# Clone fresh project
git clone https://github.com/your-username/your-repo.git live_portfolio
cd live_portfolio

# Copy backup script from old project
cp ../live_portfolio_backup_*/backup_restore_database.sh .
chmod +x backup_restore_database.sh
```

### Step 3: Setup Environment
```bash
# Copy your production .env file
cp ../live_portfolio_backup_*/.env .

# Or create new .env with your settings
nano .env
```

### Step 4: Restore Database
```bash
# Use the safe backup path from Step 1
./backup_restore_database.sh restore-from-migration /tmp/mysql_migration_YYYYMMDD_HHMMSS

# Wait for containers to start
docker compose ps
```

## Method 2: Quick Volume Copy

### Step 1: Stop Containers & Export Volume
```bash
# Stop containers
docker compose down

# Export MySQL volume to safe location
BACKUP_DIR="/tmp/mysql_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Export volume data
docker run --rm \
  -v live_portfolio_mysql_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine cp -r /data/. /backup/

echo "Database backed up to: $BACKUP_DIR"
```

### Step 2: Clone Fresh Project
```bash
cd ..
mv live_portfolio live_portfolio_old
git clone your-repo.git live_portfolio
cd live_portfolio
```

### Step 3: Restore Volume
```bash
# Create new volume
docker volume create live_portfolio_mysql_data

# Restore data
docker run --rm \
  -v live_portfolio_mysql_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine cp -r /backup/. /data/

# Start containers
docker compose up -d
```

## Method 3: SQL Dump (Safest but slower)

### Step 1: Create SQL Backup
```bash
# While containers are running
./backup_restore_database.sh backup

# This creates: ./database_backups/mysql_backup_YYYYMMDD_HHMMSS.sql
```

### Step 2: Clone Fresh Project
```bash
cd ..
mv live_portfolio live_portfolio_old
git clone your-repo.git live_portfolio
cd live_portfolio

# Copy backup files
cp -r ../live_portfolio_old/database_backups .
```

### Step 3: Restore from SQL
```bash
# Start fresh containers
docker compose up -d

# Wait for MySQL to be ready
sleep 30

# Restore database
./backup_restore_database.sh restore
# Select your backup file when prompted
```

## 🚀 Complete Production Deployment Steps

### 1. Pre-deployment Backup
```bash
./backup_restore_database.sh backup
```

### 2. Update Code
```bash
git pull origin main
# OR use migration method above for fresh clone
```

### 3. Update Environment
```bash
# Make sure .env has production settings
DEBUG=False
REDIS_URL=redis://redis:6379/0
# ... other production settings
```

### 4. Deploy
```bash
# Stop containers
docker compose down

# Clean up (optional)
docker system prune -f

# Start with new code
docker compose up --build -d

# Check status
docker compose ps
docker compose logs
```

### 5. Verify Services
```bash
# Check all services are healthy
docker compose ps

# Test database connection
docker compose exec mysql mysqladmin ping -uroot -p${MYSQL_ROOT_PASSWORD}

# Test Redis connection  
docker compose exec redis redis-cli ping

# Test Celery worker
docker compose exec celery celery -A portfolio_django inspect ping
```

## 📁 Important Files to Backup

### Always backup these before deployment:
- **Database**: MySQL volume or SQL dump
- **Environment**: `.env` file
- **Static files**: `./staticfiles/` (if customized)
- **Media files**: `./mediafiles/` (user uploads)
- **SSL certificates**: `./certbot/conf/` (if using HTTPS)
- **Nginx config**: `./nginx/` (if customized)
- **Logs**: `./logs/` (for debugging)

### Backup command:
```bash
# Create complete backup
tar -czf production_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  .env \
  staticfiles/ \
  mediafiles/ \
  certbot/ \
  nginx/ \
  logs/ \
  database_backups/
```

## 🔧 Troubleshooting

### If MySQL fails to start:
```bash
# Remove volume and start fresh
docker compose down
docker volume rm live_portfolio_mysql_data
docker compose up -d mysql

# Then restore from backup
./backup_restore_database.sh restore
```

### If containers are unhealthy:
```bash
# Check logs
docker compose logs mysql
docker compose logs redis
docker compose logs celery

# Restart specific service
docker compose restart mysql
```

### If deployment fails:
```bash
# Rollback to backup
cd ../live_portfolio_backup_YYYYMMDD
docker compose up -d
```

## 📊 Monitoring Commands

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f

# Check resource usage
docker stats

# Check volumes
docker volume ls

# Check networks
docker network ls
```