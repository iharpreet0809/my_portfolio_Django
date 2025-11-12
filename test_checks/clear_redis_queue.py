#!/usr/bin/env python
"""
Script to clear Redis queues and remove old Celery tasks.
"""

import redis
import sys

def clear_redis_queues():
    """Clear all Celery queues in Redis."""
    try:
        # Connect to Redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=0)
        
        # Test connection
        r.ping()
        print("✅ Connected to Redis")
        
        # Get all keys
        keys = r.keys('*')
        print(f"📋 Found {len(keys)} keys in Redis")
        
        if keys:
            # Show some keys for reference
            print("\n🔍 Sample keys:")
            for key in keys[:5]:
                print(f"   • {key.decode('utf-8')}")
            if len(keys) > 5:
                print(f"   ... and {len(keys) - 5} more")
            
            # Ask for confirmation
            response = input(f"\n❓ Clear all {len(keys)} keys? (y/N): ").strip().lower()
            
            if response in ['y', 'yes']:
                # Clear all keys
                r.flushdb()
                print("🧹 All Redis keys cleared!")
            else:
                print("❌ Operation cancelled")
        else:
            print("✨ Redis is already clean - no keys found")
            
    except redis.ConnectionError:
        print("❌ Could not connect to Redis")
        print("💡 Make sure Redis is running in WSL:")
        print("   wsl -d Ubuntu")
        print("   sudo service redis-server start")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🧹 REDIS QUEUE CLEANER")
    print("=" * 40)
    clear_redis_queues()