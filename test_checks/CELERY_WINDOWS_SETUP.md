# Celery Setup for Windows with WSL Redis

## Prerequisites

1. **Install Redis in WSL** (if not already done):
   ```bash
   # In WSL terminal
   sudo apt update
   sudo apt install redis-server
   ```

2. **Install Python dependencies**:
   ```bash
   pip install celery redis
   ```

## Starting Redis in WSL

1. Open WSL terminal:
   ```bash
   wsl -d Ubuntu
   ```

2. Start Redis server:
   ```bash
   sudo service redis-server start
   ```

3. Verify Redis is running:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

4. **Optional**: Check Redis status:
   ```bash
   sudo service redis-server status
   ```

## Running Celery on Windows

### Method 1: Using the Batch File (Recommended)
1. Double-click `start_celery_windows.bat`
2. The script will check Redis connection and start Celery worker

### Method 2: Using Command Prompt
1. Open Command Prompt in your project directory
2. Run:
   ```cmd
   python -m celery -A portfolio_django worker --loglevel=info --concurrency=2 --queues=default,emails
   ```

### Method 3: Using the Python Script
1. Run:
   ```cmd
   python start_celery.py
   ```

## Testing the Setup

1. **Start Redis in WSL**:
   ```bash
   wsl -d Ubuntu
   sudo service redis-server start
   ```

2. **Start Celery worker** (in Windows):
   - Double-click `start_celery_windows.bat`, or
   - Run `python start_celery.py`

3. **Test async tasks**:
   ```cmd
   python test_celery_async.py
   ```

4. **Submit a contact form** on your website and watch the Celery logs

## Troubleshooting

### Redis Connection Issues
- **Error**: `redis.exceptions.ConnectionError`
- **Solution**: Make sure Redis is running in WSL:
  ```bash
  wsl -d Ubuntu
  sudo service redis-server start
  ```

### Port Issues
- **Error**: Connection refused on port 6379
- **Solution**: Check if WSL is forwarding the port correctly:
  ```bash
  # In WSL
  netstat -tlnp | grep 6379
  ```

### Celery Import Issues
- **Error**: `ModuleNotFoundError: No module named 'celery'`
- **Solution**: Install Celery:
  ```cmd
  pip install celery redis
  ```

## Configuration Details

- **Redis URL**: `redis://127.0.0.1:6379/0`
- **Celery Broker**: Redis (same as above)
- **Queues**: `default`, `emails`
- **Concurrency**: 2 workers
- **Serializer**: JSON

## Auto-start Redis (Optional)

To automatically start Redis when WSL starts, add this to your WSL `~/.bashrc`:

```bash
# Auto-start Redis
if ! pgrep -x "redis-server" > /dev/null; then
    sudo service redis-server start
fi
```

## Monitoring

- **Celery Flower** (Web UI for monitoring):
  ```cmd
  pip install flower
  python -m celery -A portfolio_django flower
  ```
  Then visit: http://localhost:5555