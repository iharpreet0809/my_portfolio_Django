#!/bin/bash

echo "🔍 PRODUCTION EMAIL DEBUG SCRIPT"
echo "================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo ""
print_info "1. CHECKING CONTAINER STATUS"
echo "============================="
docker compose ps

echo ""
print_info "2. CHECKING CELERY WORKER LOGS (Last 20 lines)"
echo "=============================================="
docker logs celery-worker --tail=20

echo ""
print_info "3. CHECKING DJANGO APP LOGS (Last 10 lines)"
echo "=========================================="
docker logs django-app --tail=10

echo ""
print_info "4. TESTING REDIS CONNECTION"
echo "=========================="
docker compose exec redis redis-cli ping

echo ""
print_info "5. TESTING CELERY WORKER STATUS"
echo "============================="
docker compose exec celery celery -A portfolio_django inspect ping

echo ""
print_info "6. CHECKING EMAIL SETTINGS IN CONTAINER"
echo "======================================"
docker compose exec django python -c "
from django.conf import settings
print('EMAIL_HOST:', settings.EMAIL_HOST)
print('EMAIL_PORT:', settings.EMAIL_PORT)
print('EMAIL_HOST_USER:', settings.EMAIL_HOST_USER)
print('EMAIL_HOST_PASSWORD:', '*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET')
print('REDIS_URL:', settings.REDIS_URL)
"

echo ""
print_info "7. TESTING EMAIL FUNCTIONALITY"
echo "============================"
docker compose exec django python test_email_production.py

echo ""
print_info "8. CHECKING RECENT CELERY TASKS"
echo "============================="
docker compose exec django python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_django.settings')
django.setup()

from portfolio_django.celery import app
inspect = app.control.inspect()

# Check active tasks
active = inspect.active()
if active:
    print('Active tasks:', active)
else:
    print('No active tasks')

# Check reserved tasks
reserved = inspect.reserved()
if reserved:
    print('Reserved tasks:', reserved)
else:
    print('No reserved tasks')
"

echo ""
print_info "DEBUGGING COMPLETE"
echo "=================="
echo "If emails are not working, common issues:"
echo "1. Gmail App Password expired or incorrect"
echo "2. Celery worker not processing tasks"
echo "3. Redis connection issues"
echo "4. Django email settings misconfigured"