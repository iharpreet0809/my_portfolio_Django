#!/bin/bash

echo "⚠️ Cleaning up dangling images..."
docker image prune -f

echo "🧼 Cleaning up unused images (not used by any container)..."
docker image prune -a -f

echo "✅ Docker image cleanup complete."
