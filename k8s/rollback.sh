#!/bin/bash
# Rollback script for Kubernetes deployment

set -e

echo "⏪ Rolling back deployment..."

# Rollback Django
echo "🐍 Rolling back Django..."
kubectl rollout undo deployment/django -n portfolio

# Rollback Celery Worker
echo "⚙️  Rolling back Celery Worker..."
kubectl rollout undo deployment/celery-worker -n portfolio

# Rollback Celery Beat
echo "⏰ Rolling back Celery Beat..."
kubectl rollout undo deployment/celery-beat -n portfolio

# Rollback Nginx
echo "🌐 Rolling back Nginx..."
kubectl rollout undo deployment/nginx -n portfolio

echo ""
echo "✅ Rollback complete!"
echo ""
echo "📊 Current status:"
kubectl get deployments -n portfolio
