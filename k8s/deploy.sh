#!/bin/bash
# Production Kubernetes Deployment Script for iharpreet.com

set -e

echo "🚀 Starting Kubernetes deployment for iharpreet.com..."

# Apply namespace first
echo "📦 Creating namespace..."
kubectl apply -f base/namespace.yaml

# Apply ConfigMap and Secrets
echo "🔧 Applying ConfigMap and Secrets..."
kubectl apply -f base/configmap.yaml
kubectl apply -f base/secret.yaml

# Deploy MySQL StatefulSet
echo "🗄️  Deploying MySQL..."
kubectl apply -f base/mysql-statefulset.yaml

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
kubectl wait --for=condition=ready pod -l app=mysql -n portfolio --timeout=300s

# Deploy Redis
echo "📮 Deploying Redis..."
kubectl apply -f base/redis-deployment.yaml

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n portfolio --timeout=120s

# Deploy Django application
echo "🐍 Deploying Django application..."
kubectl apply -f base/django-deployment.yaml

# Wait for Django to be ready
echo "⏳ Waiting for Django to be ready..."
kubectl wait --for=condition=ready pod -l app=django -n portfolio --timeout=300s

# Deploy Celery Worker
echo "⚙️  Deploying Celery Worker..."
kubectl apply -f base/celery-worker-deployment.yaml

# Deploy Celery Beat
echo "⏰ Deploying Celery Beat..."
kubectl apply -f base/celery-beat-deployment.yaml

# Deploy Nginx
echo "🌐 Deploying Nginx..."
kubectl apply -f base/nginx-deployment.yaml

# Deploy Certbot CronJob
echo "🔒 Deploying Certbot renewal job..."
kubectl apply -f base/certbot-cronjob.yaml

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Checking deployment status..."
kubectl get all -n portfolio

echo ""
echo "🌐 To get the LoadBalancer IP for your domain:"
echo "   kubectl get svc nginx -n portfolio"
echo ""
echo "📝 Next steps:"
echo "   1. Point iharpreet.com DNS to the LoadBalancer IP"
echo "   2. Run initial SSL certificate setup (see certbot-init.sh)"
echo "   3. Monitor logs: kubectl logs -f deployment/django -n portfolio"
