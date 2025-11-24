# Kubernetes Deployment for iharpreet.com

Production-ready Kubernetes manifests for deploying the Django portfolio application.

## Architecture

- **Django**: 2 replicas with Gunicorn
- **MySQL**: StatefulSet with persistent storage
- **Redis**: Single instance with persistent storage
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled task management
- **Nginx**: 2 replicas as reverse proxy with SSL
- **Certbot**: Automated SSL certificate renewal

## Prerequisites

1. Kubernetes cluster (EKS, GKE, AKS, or self-hosted)
2. kubectl configured to access your cluster
3. Domain DNS pointing to cluster LoadBalancer IP
4. Persistent volume provisioner (for PVCs)

## Quick Start

### 1. Update Secrets

Edit `base/secret.yaml` with your actual production values:

```bash
# IMPORTANT: Never commit real secrets to Git!
# Use Kubernetes secrets management or external secret stores
```

### 2. Deploy Everything

```bash
cd k8s
chmod +x deploy.sh certbot-init.sh
./deploy.sh
```

### 3. Get LoadBalancer IP

```bash
kubectl get svc nginx -n portfolio
```

Point your DNS records:
- `iharpreet.com` → LoadBalancer IP
- `www.iharpreet.com` → LoadBalancer IP

### 4. Setup SSL Certificates

Wait for DNS propagation (5-30 minutes), then:

```bash
./certbot-init.sh
```

## Manual Deployment Steps

If you prefer step-by-step deployment:

```bash
# 1. Create namespace
kubectl apply -f base/namespace.yaml

# 2. Apply config and secrets
kubectl apply -f base/configmap.yaml
kubectl apply -f base/secret.yaml

# 3. Deploy databases
kubectl apply -f base/mysql-statefulset.yaml
kubectl apply -f base/redis-deployment.yaml

# 4. Deploy application
kubectl apply -f base/django-deployment.yaml
kubectl apply -f base/celery-worker-deployment.yaml
kubectl apply -f base/celery-beat-deployment.yaml

# 5. Deploy web server
kubectl apply -f base/nginx-deployment.yaml

# 6. Setup SSL renewal
kubectl apply -f base/certbot-cronjob.yaml
```

## Useful Commands

### Check Status
```bash
kubectl get all -n portfolio
kubectl get pvc -n portfolio
```

### View Logs
```bash
# Django logs
kubectl logs -f deployment/django -n portfolio

# Celery worker logs
kubectl logs -f deployment/celery-worker -n portfolio

# Nginx logs
kubectl logs -f deployment/nginx -n portfolio
```

### Scale Services
```bash
# Scale Django replicas
kubectl scale deployment django --replicas=3 -n portfolio

# Scale Celery workers
kubectl scale deployment celery-worker --replicas=2 -n portfolio
```

### Update Application
```bash
# Update to new image version
kubectl set image deployment/django django=harpreetdevops/portfolio:v2.0 -n portfolio

# Restart deployment
kubectl rollout restart deployment/django -n portfolio
```

### Database Operations
```bash
# Connect to MySQL
kubectl exec -it mysql-0 -n portfolio -- mysql -u admin -p

# Run Django migrations
kubectl exec -it deployment/django -n portfolio -- python manage.py migrate

# Create superuser
kubectl exec -it deployment/django -n portfolio -- python manage.py createsuperuser
```

### Troubleshooting
```bash
# Describe pod issues
kubectl describe pod <pod-name> -n portfolio

# Get events
kubectl get events -n portfolio --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n portfolio
```

## Resource Requirements

Minimum cluster resources:
- **CPU**: 2 cores
- **Memory**: 2GB RAM
- **Storage**: 25GB

Recommended for production:
- **CPU**: 4+ cores
- **Memory**: 4GB+ RAM
- **Storage**: 50GB+

## Security Notes

1. **Secrets Management**: Use external secret management (AWS Secrets Manager, HashiCorp Vault, etc.)
2. **Network Policies**: Add network policies to restrict pod-to-pod communication
3. **RBAC**: Configure proper role-based access control
4. **Image Security**: Scan images for vulnerabilities before deployment
5. **SSL/TLS**: Certificates auto-renew via CronJob every 12 hours

## Monitoring

Consider adding:
- Prometheus for metrics
- Grafana for visualization
- ELK/EFK stack for log aggregation
- Jaeger for distributed tracing

## Backup Strategy

1. **Database**: Schedule MySQL backups using CronJob
2. **Persistent Volumes**: Snapshot PVCs regularly
3. **Configuration**: Keep manifests in version control

## Production Checklist

- [ ] Update all secrets in `secret.yaml`
- [ ] Configure proper resource limits
- [ ] Setup monitoring and alerting
- [ ] Configure backup strategy
- [ ] Test disaster recovery
- [ ] Setup CI/CD pipeline
- [ ] Configure autoscaling (HPA)
- [ ] Review security policies
- [ ] Setup log aggregation
- [ ] Document runbooks

## Support

For issues or questions, check:
- Application logs: `kubectl logs -f deployment/django -n portfolio`
- Kubernetes events: `kubectl get events -n portfolio`
- Pod status: `kubectl describe pod <pod-name> -n portfolio`
