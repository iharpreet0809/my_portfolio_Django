#!/bin/bash

echo "⚠️ Cleaning up dangling images..."
docker image prune -f

echo "🧼 Cleaning up unused images (not used by any container)..."
docker image prune -a -f

echo "✅ Docker image cleanup complete."

# Make it executable:
# chmod +x docker-cleanup.sh


# Run it periodically or after big rebuilds:
# ./docker-cleanup.sh
