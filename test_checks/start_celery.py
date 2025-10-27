#!/usr/bin/env python
"""
Script to start Celery worker for development.
Run this in a separate terminal window.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_redis_connection():
    """Check if Redis is accessible."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("💡 Make sure Redis is running in WSL:")
        print("   wsl -d Ubuntu")
        print("   sudo service redis-server start")
        return False

def start_celery_worker():
    """Start Celery worker."""
    print("🚀 Starting Celery Worker...")
    print("-" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found. Run this script from project root.")
        return False
    
    # Check Redis connection first
    if not check_redis_connection():
        return False
    
    print("📋 Celery Worker Configuration:")
    print("   • Broker: Redis (localhost:6379)")
    print("   • Concurrency: 2 workers")
    print("   • Log Level: INFO")
    print("   • Queues: default, emails")
    print()
    
    try:
        # Start Celery worker
        cmd = [
            sys.executable, '-m', 'celery', 
            '-A', 'portfolio_django',
            'worker',
            '--loglevel=info',
            '--concurrency=2',
            '--queues=default,emails'
        ]
        
        print("🔄 Starting Celery worker...")
        print("💡 Press Ctrl+C to stop the worker")
        print("=" * 60)
        
        # Run Celery worker
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Celery worker stopped by user")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Celery worker: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    print("🎯 CELERY WORKER STARTER")
    print("=" * 60)
    
    print("📝 Instructions:")
    print("1. Make sure Redis is running in WSL")
    print("2. Keep this terminal open while testing")
    print("3. Submit contact form in another terminal/browser")
    print("4. Watch for async email processing logs")
    print()
    
    start_celery_worker()

if __name__ == "__main__":
    main()