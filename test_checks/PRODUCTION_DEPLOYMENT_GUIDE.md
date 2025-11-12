# 🚀 Production Deployment Guide

## 📋 **Pre-Deployment Checklist**

### **1. Environment Setup**
```bash
# Copy production environment file
cp .env.production .env

# Update .env with your actual values:
# - SECRET_KEY (generate new one)
# - EMAIL_HOST_PASSWORD (your Gmail app password)
# - ALLOWED_HOSTS (your domain)
# - CSRF_TRUSTED_ORIGINS (your domain with https)
```

### **2. Git Push (if needed)**
```bash
git add .
git commit -m "Production ready with Celery and Redis"
git push origin main
```

## 🐳 **Docker Deployment Commands**

### **Method 1: Automated Deployment (Recommended)**
```bash
# One-command deployment
python deploy_production.py
```

### **Method 2: Manual Deployment**
```bash
# Clean up existing containers
docker-compose down
docker system prune -f

# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps
```

## 🔧 **Services Included**

### **1. Web Application (Django)**
- **Port**: 8000
- **Features**: Contact form, portfolio, admin panel
- **Performance**: Optimized with lazy loading, caching

### **2. Database (MySQL)**
- **Port**: 3306
- **Persistent**: Data stored in Docker volume
- **Auto-migration**: Runs on startup

### **3. Redis (Message Broker)**
- **Port**: 6379
- **Purpose**: Celery task queue
- **Persistent**: Data stored in Docker volume

### **4. Celery Worker**
- **Purpose**: Async email processing
- **Concurrency**: 2 workers
- **Auto-restart**: Yes

### **5. Celery Beat (Optional)**
- **Purpose**: Scheduled tasks
- **Status**: Ready for future use

## 📊 **Verification Steps**

### **1. Check All Services Running**
```bash
docker-compose ps
# Should show: web, db, redis, celery all "Up"
```

### **2. Test Web Application**
```bash
# Open browser
http://localhost:8000

# Submit contact form - should work with async email
```

### **3. Check Celery Worker**
```bash
# View Celery logs
docker-compose logs -f celery

# Should show: "celery@container ready"
```

### **4. Test Redis Connection**
```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

## 🐛 **Troubleshooting**

### **Problem: Services not starting**
```bash
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart web
```

### **Problem: Database connection error**
```bash
# Wait for MySQL to fully start
docker-compose logs db

# Restart web service after DB is ready
docker-compose restart web
```

### **Problem: Celery not working**
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Check Celery worker logs
docker-compose logs celery

# Restart Celery
docker-compose restart celery
```

### **Problem: Email not sending**
```bash
# Check environment variables
docker-compose exec web env | grep EMAIL

# Test email configuration
docker-compose exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

## 📈 **Performance Features Active**

### **✅ Optimizations Included:**
- Lazy loading for images
- Async CSS/JS loading
- Gzip compression
- Database caching
- Async email processing
- Static file optimization

### **📊 Expected Performance:**
- **Page Load**: 2-4 seconds (after image optimization)
- **Contact Form**: 0.1-0.2 second response (async)
- **Email Delivery**: Background processing
- **User Experience**: Excellent

## 🔄 **Common Operations**

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery
```

### **Restart Services**
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart web
```

### **Update Code**
```bash
# After code changes
docker-compose down
docker-compose up -d --build
```

### **Database Operations**
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Django shell
docker-compose exec web python manage.py shell
```

### **Stop Everything**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (careful!)
docker-compose down -v
```

## 🎯 **Production Checklist**

- [ ] `.env` file configured with production values
- [ ] `DEBUG=False` in environment
- [ ] Secret key changed from default
- [ ] Email password configured
- [ ] Domain added to ALLOWED_HOSTS
- [ ] All services running (`docker-compose ps`)
- [ ] Web app accessible (http://localhost:8000)
- [ ] Contact form working with async email
- [ ] Celery worker processing tasks
- [ ] Redis responding to ping
- [ ] Database migrations applied

## 🚀 **Final Result**

After successful deployment:
- ✅ **Portfolio website** running on port 8000
- ✅ **Contact form** with async email processing
- ✅ **Performance optimized** for fast loading
- ✅ **Production ready** with proper error handling
- ✅ **Scalable architecture** with Celery and Redis

---

**🎉 Your portfolio is now production-ready with async email processing!**