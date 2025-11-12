@echo off
echo ========================================
echo    CELERY WORKER STARTER (Windows)
echo ========================================
echo.

echo Checking Redis connection...
python -c "import redis; r = redis.Redis(host='127.0.0.1', port=6379, db=0); r.ping(); print('✅ Redis connected successfully')" 2>nul
if errorlevel 1 (
    echo ❌ Redis connection failed!
    echo.
    echo 💡 To start Redis in WSL:
    echo    1. Open WSL terminal: wsl -d Ubuntu
    echo    2. Start Redis: sudo service redis-server start
    echo    3. Verify: redis-cli ping
    echo.
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Celery Worker...
echo Configuration:
echo   • Broker: Redis (127.0.0.1:6379)
echo   • Queues: default, emails
echo   • Concurrency: 2 workers
echo   • Log Level: INFO
echo.
echo 💡 Press Ctrl+C to stop the worker
echo ========================================
echo.

python -m celery -A portfolio_django worker --loglevel=info --concurrency=2 --queues=default,emails

echo.
echo 🛑 Celery worker stopped
pause