# Kubernetes Files Application Order

This document explains the correct order to apply Kubernetes manifests and why.

## 📋 Application Order

### Phase 1: Foundation (Namespace & Configuration)

```bash
kubectl apply -f base/namespace.yaml
kubectl apply -f base/configmap.yaml
kubectl apply -f base/secret.yaml
```

**Why this order?**
- Namespace must exist before any other resources
- ConfigMap and Secrets must exist before pods reference them

### Phase 2: Data Layer (Databases & Cache)

```bash
kubectl apply -f base/mysql-statefulset.yaml
kubectl apply -f base/redis-deployment.yaml
```

**Why this order?**
- MySQL and Redis must be running before application pods start
- StatefulSet creates persistent storage automatically
- Wait for these to be healthy before proceeding

**Verify:**
```bash
kubectl wait --for=condition=ready pod -l app=mysql -n portfolio --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n portfolio --timeout=120s
```

### Phase 3: Application Layer (Django & Celery)

```bash
kubectl apply -f base/django-deployment.yaml
kubectl apply -f base/celery-worker-deployment.yaml
kubectl apply -f base/celery-beat-deployment.yaml
```

**Why this order?**
- Django needs MySQL and Redis (init containers handle waiting)
- Celery workers need Django code, MySQL, and Redis
- Celery beat needs MySQL for schedule storage

**Verify:**
```bash
kubectl wait --for=condition=ready pod -l app=django -n portfolio --timeout=300s
```

### Phase 4: Web Layer (Nginx)

```bash
kubectl apply -f base/nginx-deployment.yaml
```

**Why last?**
- Nginx proxies to Django, so Django must be running first
- Creates LoadBalancer (gets external IP)
- Serves static files from shared volume

**Verify:**
```bash
kubectl get svc nginx -n portfolio
```

### Phase 5: SSL Automation (Certbot)

```bash
kubectl apply -f base/certbot-cronjob.yaml
```

**Why after Nginx?**
- CronJob runs periodically (not immediately)
- Needs Nginx to serve ACME challenges
- Initial certificate setup uses `certbot-init.sh` script

## 🔄 Dependency Graph

```
namespace.yaml
    ↓
configmap.yaml + secret.yaml
    ↓
mysql-statefulset.yaml + redis-deployment.yaml
    ↓
django-deployment.yaml
    ↓
celery-worker-deployment.yaml + celery-beat-deployment.yaml
    ↓
nginx-deployment.yaml
    ↓
certbot-cronjob.yaml
```

## 📝 Manual Application (Step-by-Step)

If you want to apply files manually instead of using `deploy.sh`:

```bash
# Step 1: Create namespace
kubectl apply -f base/namespace.yaml
echo "✅ Namespace created"

# Step 2: Apply configuration
kubectl apply -f base/configmap.yaml
kubectl apply -f base/secret.yaml
echo "✅ Configuration applied"

# Step 3: Deploy MySQL
kubectl apply -f base/mysql-statefulset.yaml
echo "⏳ Waiting for MySQL..."
kubectl wait --for=condition=ready pod -l app=mysql -n portfolio --timeout=300s
echo "✅ MySQL ready"

# Step 4: Deploy Redis
kubectl apply -f base/redis-deployment.yaml
echo "⏳ Waiting for Redis..."
kubectl wait --for=condition=ready pod -l app=redis -n portfolio --timeout=120s
echo "✅ Redis ready"

# Step 5: Deploy Django
kubectl apply -f base/django-deployment.yaml
echo "⏳ Waiting for Django..."
kubectl wait --for=condition=ready pod -l app=django -n portfolio --timeout=300s
echo "✅ Django ready"

# Step 6: Deploy Celery
kubectl apply -f base/celery-worker-deployment.yaml
kubectl apply -f base/celery-beat-deployment.yaml
echo "✅ Celery deployed"

# Step 7: Deploy Nginx
kubectl apply -f base/nginx-deployment.yaml
echo "⏳ Waiting for Nginx..."
kubectl wait --for=condition=ready pod -l app=nginx -n portfolio --timeout=120s
echo "✅ Nginx ready"

# Step 8: Setup SSL renewal
kubectl apply -f base/certbot-cronjob.yaml
echo "✅ Certbot CronJob created"

# Step 9: Check everything
kubectl get all -n portfolio
```

## 🔄 Update Order

When updating existing deployments:

### Update Application Code (Django/Celery)

```bash
# 1. Update Django first
kubectl set image deployment/django django=harpreetdevops/portfolio:v2.0 -n portfolio

# 2. Wait for Django rollout
kubectl rollout status deployment/django -n portfolio

# 3. Update Celery worker
kubectl set image deployment/celery-worker celery-worker=harpreetdevops/portfolio:v2.0 -n portfolio

# 4. Update Celery beat
kubectl set image deployment/celery-beat celery-beat=harpreetdevops/portfolio:v2.0 -n portfolio
```

### Update Configuration

```bash
# 1. Update ConfigMap or Secret
kubectl apply -f base/configmap.yaml

# 2. Restart deployments to pick up changes
kubectl rollout restart deployment/django -n portfolio
kubectl rollout restart deployment/celery-worker -n portfolio
kubectl rollout restart deployment/celery-beat -n portfolio
```

### Update Nginx Configuration

```bash
# 1. Update ConfigMap
kubectl apply -f base/nginx-deployment.yaml

# 2. Restart Nginx
kubectl rollout restart deployment/nginx -n portfolio
```

## 🗑️ Deletion Order

When removing resources (reverse order):

```bash
# 1. Remove CronJob
kubectl delete -f base/certbot-cronjob.yaml

# 2. Remove Nginx
kubectl delete -f base/nginx-deployment.yaml

# 3. Remove Celery
kubectl delete -f base/celery-beat-deployment.yaml
kubectl delete -f base/celery-worker-deployment.yaml

# 4. Remove Django
kubectl delete -f base/django-deployment.yaml

# 5. Remove databases
kubectl delete -f base/redis-deployment.yaml
kubectl delete -f base/mysql-statefulset.yaml

# 6. Remove configuration
kubectl delete -f base/secret.yaml
kubectl delete -f base/configmap.yaml

# 7. Remove namespace (deletes everything)
kubectl delete -f base/namespace.yaml
```

**Or use the cleanup script:**
```bash
./cleanup.sh
```

## ⚠️ Important Notes

### Init Containers

Django, Celery Worker, and Celery Beat have init containers that wait for MySQL and Redis. This means:
- You don't need to manually wait between steps when using `deploy.sh`
- Pods will automatically wait for dependencies
- If MySQL/Redis aren't ready, pods will stay in `Init:0/2` state

### StatefulSet vs Deployment

- **MySQL** uses StatefulSet (stable identity, ordered deployment)
- **Others** use Deployment (stateless, can scale freely)

### Persistent Volumes

PVCs are created automatically by:
- StatefulSet (mysql-data)
- Deployment manifests (staticfiles, logs, certbot volumes)

### Service Dependencies

```
Internet → LoadBalancer (nginx service)
         → Nginx pods
         → ClusterIP (django service)
         → Django pods
         → ClusterIP (mysql/redis services)
         → MySQL/Redis pods
```

## 🎯 Best Practices

1. **Always apply namespace first**
2. **Wait for databases to be ready** before checking application
3. **Use `deploy.sh`** for automated deployment
4. **Check logs** if pods don't start: `kubectl logs <pod-name> -n portfolio`
5. **Use `kubectl get events`** to see what's happening
6. **Apply updates during low-traffic periods**
7. **Test in staging environment first**

## 📊 Verification Commands

After each phase:

```bash
# Check all resources
kubectl get all -n portfolio

# Check pods status
kubectl get pods -n portfolio

# Check services
kubectl get svc -n portfolio

# Check persistent volumes
kubectl get pvc -n portfolio

# Check events
kubectl get events -n portfolio --sort-by='.lastTimestamp'

# Check specific pod logs
kubectl logs <pod-name> -n portfolio
```

---

**For automated deployment, use:** `./deploy.sh`

**For detailed guide, see:** [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md)
