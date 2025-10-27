#!/bin/bash

echo "Starting Celery Worker for Portfolio Django Application..."
echo ""
echo "Make sure Redis is running before starting this script."
echo ""
echo "Press Ctrl+C to stop the worker."
echo ""

celery -A portfolio_django worker --loglevel=info


