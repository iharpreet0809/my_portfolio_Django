#!/usr/bin/env python
"""
Production Email Testing Script
Run this on EC2 to test email functionality
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_django.settings')
django.setup()

def test_email_settings():
    """Test email configuration"""
    print("🔧 EMAIL CONFIGURATION TEST")
    print("=" * 40)
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print()

def test_celery_connection():
    """Test Celery connection"""
    print("🔧 CELERY CONNECTION TEST")
    print("=" * 40)
    
    try:
        from portfolio_django.celery import app
        
        # Test Celery connection
        inspect = app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✅ Celery workers are running:")
            for worker, info in stats.items():
                print(f"   • {worker}: {info.get('pool', {}).get('max-concurrency', 'N/A')} workers")
        else:
            print("❌ No Celery workers found")
            
        return bool(stats)
    except Exception as e:
        print(f"❌ Celery connection failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("🔧 REDIS CONNECTION TEST")
    print("=" * 40)
    
    try:
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✅ Redis connection successful")
        
        # Check Redis info
        info = r.info()
        print(f"   • Redis version: {info.get('redis_version')}")
        print(f"   • Connected clients: {info.get('connected_clients')}")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_email_sending():
    """Test actual email sending"""
    print("🔧 EMAIL SENDING TEST")
    print("=" * 40)
    
    try:
        from django.core.mail import EmailMessage
        
        # Test email
        email = EmailMessage(
            subject='Test Email from Production',
            body='This is a test email to verify email functionality is working.',
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER],  # Send to self
        )
        
        email.send()
        print("✅ Test email sent successfully")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def test_celery_email_task():
    """Test Celery email task"""
    print("🔧 CELERY EMAIL TASK TEST")
    print("=" * 40)
    
    try:
        from portfolio_app.tasks import send_contact_email
        
        # Send test email via Celery
        result = send_contact_email.delay(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="This is a test message from Celery"
        )
        
        print(f"✅ Celery task queued: {result.id}")
        print("   Check Celery worker logs for execution status")
        return True
        
    except Exception as e:
        print(f"❌ Celery email task failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 PRODUCTION EMAIL DIAGNOSTICS")
    print("=" * 50)
    print()
    
    # Test configurations
    test_email_settings()
    
    # Test connections
    redis_ok = test_redis_connection()
    print()
    
    celery_ok = test_celery_connection()
    print()
    
    # Test email functionality
    if redis_ok and celery_ok:
        test_celery_email_task()
        print()
    
    test_email_sending()
    print()
    
    print("🎯 RECOMMENDATIONS:")
    print("=" * 50)
    
    if not redis_ok:
        print("❌ Fix Redis connection first")
    elif not celery_ok:
        print("❌ Fix Celery worker connection")
    else:
        print("✅ Infrastructure looks good")
        print("💡 Check Gmail App Password and 2FA settings")
        print("💡 Check Celery worker logs: docker logs celery-worker")
        print("💡 Check Django logs: docker logs django-app")

if __name__ == "__main__":
    main()