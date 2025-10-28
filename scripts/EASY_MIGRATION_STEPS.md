# 🚀 SUPER EASY MIGRATION STEPS

## What Will Be Backed Up:
- ✅ **MySQL Database** (form submissions data)
- ✅ **Redis Data** (Celery tasks)
- ✅ **SSL Certificates** (certbot folder - for HTTPS)
- ✅ **.env file** (configuration)
- ✅ **Nginx config** (if customized)

## What Will NOT Be Backed Up:
- ❌ Static files (CSS, JS, images) - these come from code
- ❌ Media files - no user uploads yet
- ❌ Logs - not essential

---

## 📋 STEP-BY-STEP PROCESS

### Step 1: Create Backup Script in Current Project
```bash
# Go to current project
cd /home/ubuntu/githubs/live_portfolio

# Create backup script
nano simple_backup_restore.sh 
#or 
vim simple_backup_restore.sh

# Copy the script content and save (Ctrl+X, Y, Enter)

# Make executable
chmod +x simple_backup_restore.sh
```

### Step 2: Backup Current Data
```bash
# Run backup (this will create backup in /home/ubuntu/data_backups/)
./simple_backup_restore.sh backup
```

**Output will show:**
```
Backup saved to: /home/ubuntu/data_backups/mysql_migration_20241027_143022
```

### Step 3: Move Current Project
```bash
# Go to parent directory
cd /home/ubuntu/githubs/

# Rename current project (as backup)
mv live_portfolio live_portfolio_old_$(date +%Y%m%d)
```

### Step 4: Clone Fresh Project
```bash
# Clone fresh code
git clone https://github.com/your-username/your-repo.git live_portfolio

# Go to new project
cd live_portfolio

# Check files
ls -la
```

### Step 5: Copy Backup Script to New Project
```bash
# Copy backup script from old project
cp ../live_portfolio_old_*/simple_backup_restore.sh .

# Make executable
chmod +x simple_backup_restore.sh
```

### Step 6: Restore Data
```bash
# Restore from backup (use the path from Step 2)
./simple_backup_restore.sh restore /home/ubuntu/data_backups/mysql_migration_20241027_143022
```

### Step 7: Verify Everything Works
```bash
# Check all containers are running
docker compose ps

# Check website
curl -I http://your-domain.com

# Check database
docker compose exec mysql mysqladmin ping -uroot -p${MYSQL_ROOT_PASSWORD}
```

---

## 🎯 QUICK COMMANDS (Copy-Paste Ready)

### Complete Migration in 6 Commands:
```bash
# 1. Backup
cd /home/ubuntu/githubs/live_portfolio
./simple_backup_restore.sh backup

# 2. Move old project
cd ..
mv live_portfolio live_portfolio_old_$(date +%Y%m%d)

# 3. Clone fresh
git clone https://github.com/your-username/your-repo.git live_portfolio
cd live_portfolio

# 4. Copy script
cp ../live_portfolio_old_*/simple_backup_restore.sh .
chmod +x simple_backup_restore.sh

# 5. Restore (replace YYYYMMDD_HHMMSS with actual backup folder name)
./simple_backup_restore.sh restore /home/ubuntu/data_backups/mysql_migration_YYYYMMDD_HHMMSS

# 6. Verify
docker compose ps
```

---

## 🔧 If Something Goes Wrong (Rollback)

```bash
# Stop new project
cd /home/ubuntu/githubs/live_portfolio
docker compose down

# Remove new project
cd ..
rm -rf live_portfolio

# Restore old project
mv live_portfolio_old_* live_portfolio
cd live_portfolio

# Start old project
docker compose up -d
```

---

## 📁 Backup Location Structure

```
/home/ubuntu/data_backups/
└── mysql_migration_20241027_143022/
    ├── mysql_backup.sql          # SQL dump
    ├── mysql_volume.tar.gz       # MySQL volume data
    ├── redis_data.tar.gz         # Redis data
    ├── .env                      # Environment config
    ├── certbot/                  # SSL certificates
    └── nginx/                    # Nginx config
```

---

## ⏱️ Time Required
- **Backup**: ~2-3 minutes
- **Clone**: ~1 minute  
- **Restore**: ~3-4 minutes
- **Total**: ~6-8 minutes

---

## 🚨 Important Notes
1. **Backup path** will be shown after Step 2 - copy it exactly
2. **Replace your-repo.git** with actual GitHub repo URL
3. **Keep old project** until everything is verified working
4. **SSL certificates** will be preserved (no need to regenerate)
5. **All form data** will be preserved in MySQL