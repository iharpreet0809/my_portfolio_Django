# Complete Kubernetes Deployment Guide for iharpreet.com

This guide walks you through deploying your Django portfolio application to Kubernetes from your EC2 instance.

## 📋 Prerequisites

Before starting, ensure you have:

1. **Kubernetes Cluster** running (EKS, GKE, AKS, or self-hosted)
2. **kubectl** installed and configured
3. **Git** installed on your EC2 instance
4. **Domain DNS** ready to point to LoadBalancer IP
5. **Docker image** pushed to Docker Hub: `harpreetdevops/portfolio:latest`

## 🚀 Step-by-Step Deployment

### Step 1: Clone Repository on EC2

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Navigate to your project directory
cd /portfolio

# Or clone from GitHub if needed
git clone https://github.com/iharpreet0809/my_portfolio_Django.git
cd my_portfolio_Django
```

### Step 2: Verify kubectl Connection

```bash
# Check if kubectl is connected to your cluster
kubectl cluster-info

# Check nodes
kubectl get nodes

# If not configured, configure kubectl for your cluster:
# For EKS:
aws eks update-kubeconfig --region us-east-1 --name your-cluster-name

# For other clusters, use your kubeconfig file
export KUBECONFIG=/path/to/your/kubeconfig
```

### Step 3: Update Secrets (CRITICAL!)

```bash
# Navigate to k8s directory
cd k8s

# Edit the secret file with your actual production values
nano base/secret.yaml
# or
vim base/secret.yaml
```

**Update these values in `base/secret.yaml`:**

```yaml
stringData:
  SECRET_KEY: "your-actual-django-secret-key-here"
  MYSQL_DB: "devops"
  MYSQL_USER: "admin"
  MYSQL_PASSWORD: "your-strong-mysql-password"
  MYSQL_ROOT_PASSWORD: "your-strong-root-password"
  EMAIL_HOST_PASSWORD: "your-email-app-password"
```

**⚠️ IMPORTANT:** Never commit real secrets to Git!

### Step 4: Build and Push Docker Image (if not done)

```bash
# Go back to project root
cd ..

# Build Docker image
docker build -t harpreetdevops/portfolio:latest .

# Login to Docker Hub
docker login

# Push image
docker push harpreetdevops/portfolio:latest
```

### Step 5: Deploy to Kubernetes

```bash
# Navigate to k8s directory
cd k8s

# Make scripts executable
chmod +x *.sh

# Run the deployment script
./deploy.sh
```

**What `deploy.sh` does:**
1. Creates `portfolio` namespace
2. Applies ConfigMap and Secrets
3. Deploys MySQL StatefulSet
4. Deploys Redis
5. Deploys Django application
6. Deploys Celery Worker and Beat
7. Deploys Nginx
8. Sets up Certbot CronJob

### Step 6: Monitor Deployment

```bash
# Watch all resources being created
kubectl get all -n portfolio -w

# Check pod status
kubectl get pods -n portfolio

# Check if all pods are running
kubectl get pods -n portfolio | grep Running

# View deployment status
kubectl get deployments -n portfolio

# Check persistent volumes
kubectl get pvc -n portfolio
```

### Step 7: Get LoadBalancer IP

```bash
# Get the external IP for Nginx service
kubectl get svc nginx -n portfolio

# Output will look like:
# NAME    TYPE           CLUSTER-IP      EXTERNAL-IP                                                              PORT(S)
# nginx   LoadBalancer   10.100.123.45   a1b2c3d4e5f6g7h8i9j0.us-east-1.elb.amazonaws.com   80:30080/TCP,443:30443/TCP
```

**Copy the EXTERNAL-IP value**

### Step 8: Update DNS Records

Point your domain to the LoadBalancer IP:

**For AWS Route 53:**
```bash
# Create A record or CNAME
iharpreet.com        -> CNAME -> your-loadbalancer-dns
www.iharpreet.com    -> CNAME -> your-loadbalancer-dns
```

**For other DNS providers:**
- Create A record pointing to LoadBalancer IP
- Create CNAME for www subdomain

**Wait 5-30 minutes for DNS propagation**

### Step 9: Verify DNS Propagation

```bash
# Check if DNS is resolving
nslookup iharpreet.com

# Or use dig
dig iharpreet.com

# Test HTTP access (should redirect to HTTPS, may show cert error initially)
curl -I http://iharpreet.com
```

### Step 10: Setup SSL Certificates

Once DNS is propagated:

```bash
# Run Certbot initialization script
./certbot-init.sh
```

**This script will:**
1. Request SSL certificates from Let's Encrypt
2. Verify domain ownership via HTTP challenge
3. Store certificates in persistent volume
4. Restart Nginx to load certificates

**Monitor the process:**
```bash
# Check certbot logs
kubectl logs certbot-init -n portfolio

# After completion, verify Nginx restarted
kubectl get pods -n portfolio | grep nginx
```

### Step 11: Verify Your Site is Live

```bash
# Test HTTPS access
curl -I https://iharpreet.com

# Should return 200 OK with SSL certificate info

# Open in browser
# https://iharpreet.com
# https://www.iharpreet.com
```

### Step 12: Run Django Management Commands

```bash
# Create superuser for Django admin
kubectl exec -it deployment/django -n portfolio -- python manage.py createsuperuser

# Collect static files (if needed)
kubectl exec -it deployment/django -n portfolio -- python manage.py collectstatic --noinput

# Run migrations (if needed)
kubectl exec -it deployment/django -n portfolio -- python manage.py migrate

# Check Django status
kubectl exec -it deployment/django -n portfolio -- python manage.py check
```

## 📊 Post-Deployment Verification

### Check All Services

```bash
# View all resources
kubectl get all -n portfolio

# Check service endpoints
kubectl get endpoints -n portfolio

# View persistent volumes
kubectl get pv
kubectl get pvc -n portfolio
```

### View Logs

```bash
# Django logs
kubectl logs -f deployment/django -n portfolio

# Celery worker logs
kubectl logs -f deployment/celery-worker -n portfolio

# Celery beat logs
kubectl logs -f deployment/celery-beat -n portfolio

# Nginx logs
kubectl logs -f deployment/nginx -n portfolio

# MySQL logs
kubectl logs -f statefulset/mysql -n portfolio

# Redis logs
kubectl logs -f deployment/redis -n portfolio
```

### Test Application Features

1. **Homepage**: https://iharpreet.com
2. **Admin Panel**: https://iharpreet.com/admin
3. **Static Files**: Check CSS/JS loading
4. **Database**: Test form submissions
5. **Celery Tasks**: Test async operations
6. **Email**: Test contact form

## 🔧 Common Operations

### Scale Deployments

```bash
# Scale Django pods
kubectl scale deployment django --replicas=3 -n portfolio

# Scale Celery workers
kubectl scale deployment celery-worker --replicas=2 -n portfolio

# Scale Nginx
kubectl scale deployment nginx --replicas=3 -n portfolio
```

### Update Application

```bash
# Build new image with version tag
docker build -t harpreetdevops/portfolio:v2.0 .
docker push harpreetdevops/portfolio:v2.0

# Update deployment
kubectl set image deployment/django django=harpreetdevops/portfolio:v2.0 -n portfolio
kubectl set image deployment/celery-worker celery-worker=harpreetdevops/portfolio:v2.0 -n portfolio
kubectl set image deployment/celery-beat celery-beat=harpreetdevops/portfolio:v2.0 -n portfolio

# Check rollout status
kubectl rollout status deployment/django -n portfolio
```

### Rollback Deployment

```bash
# Rollback to previous version
./rollback.sh

# Or manually rollback specific deployment
kubectl rollout undo deployment/django -n portfolio

# Check rollout history
kubectl rollout history deployment/django -n portfolio
```

### Database Operations

```bash
# Connect to MySQL
kubectl exec -it mysql-0 -n portfolio -- mysql -u admin -p

# Backup database
kubectl exec mysql-0 -n portfolio -- mysqldump -u admin -p devops > backup.sql

# Restore database
kubectl exec -i mysql-0 -n portfolio -- mysql -u admin -p devops < backup.sql
```

### View Resource Usage

```bash
# Check pod resource usage
kubectl top pods -n portfolio

# Check node resource usage
kubectl top nodes

# Describe pod for detailed info
kubectl describe pod <pod-name> -n portfolio
```

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n portfolio

# Describe problematic pod
kubectl describe pod <pod-name> -n portfolio

# Check events
kubectl get events -n portfolio --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n portfolio
```

### Database Connection Issues

```bash
# Check MySQL is running
kubectl get pods -n portfolio | grep mysql

# Check MySQL logs
kubectl logs mysql-0 -n portfolio

# Test connection from Django pod
kubectl exec -it deployment/django -n portfolio -- nc -zv mysql 3306
```

### SSL Certificate Issues

```bash
# Check certificate files
kubectl exec deployment/nginx -n portfolio -- ls -la /etc/letsencrypt/live/iharpreet.com/

# Re-run certbot
./certbot-init.sh

# Check Nginx configuration
kubectl exec deployment/nginx -n portfolio -- nginx -t

# Restart Nginx
kubectl rollout restart deployment/nginx -n portfolio
```

### Application Errors

```bash
# Check Django logs
kubectl logs -f deployment/django -n portfolio --tail=100

# Check Django settings
kubectl exec -it deployment/django -n portfolio -- python manage.py check

# Run Django shell
kubectl exec -it deployment/django -n portfolio -- python manage.py shell
```

## 🧹 Cleanup (Remove Everything)

```bash
# Run cleanup script
./cleanup.sh

# This will delete:
# - All deployments, services, pods
# - All persistent volume claims
# - All ConfigMaps and Secrets
# - Optionally the namespace
```

## 📈 Production Best Practices

### 1. Use Specific Image Tags

Instead of `:latest`, use version tags:
```yaml
image: harpreetdevops/portfolio:v1.0.0
```

### 2. Set Resource Limits

Already configured in manifests:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 3. Enable Horizontal Pod Autoscaling

```bash
# Create HPA for Django
kubectl autoscale deployment django --cpu-percent=70 --min=2 --max=10 -n portfolio
```

### 4. Setup Monitoring

Consider adding:
- Prometheus for metrics
- Grafana for dashboards
- ELK/EFK for log aggregation

### 5. Backup Strategy

```bash
# Create backup CronJob for MySQL
# Schedule daily backups
# Store in S3 or persistent storage
```

### 6. Use External Secrets Management

Instead of storing secrets in YAML:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes External Secrets Operator

## 📞 Support & Resources

### Useful Commands Reference

```bash
# Get all resources in namespace
kubectl get all -n portfolio

# Delete specific resource
kubectl delete deployment <name> -n portfolio

# Edit resource
kubectl edit deployment django -n portfolio

# Port forward for local testing
kubectl port-forward deployment/django 8000:8000 -n portfolio

# Copy files to/from pod
kubectl cp <local-file> <pod-name>:/path/in/pod -n portfolio

# Execute command in pod
kubectl exec -it <pod-name> -n portfolio -- /bin/bash
```

### Documentation Links

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Let's Encrypt](https://letsencrypt.org/docs/)

## ✅ Deployment Checklist

- [ ] Kubernetes cluster is running
- [ ] kubectl is configured
- [ ] Docker image is built and pushed
- [ ] Secrets are updated in `base/secret.yaml`
- [ ] Deployment script executed successfully
- [ ] All pods are running
- [ ] LoadBalancer IP obtained
- [ ] DNS records updated
- [ ] DNS propagation verified
- [ ] SSL certificates obtained
- [ ] HTTPS site is accessible
- [ ] Django admin is accessible
- [ ] Static files are loading
- [ ] Database is working
- [ ] Celery tasks are processing
- [ ] Monitoring is setup
- [ ] Backups are configured

---

**Your site should now be live at https://iharpreet.com! 🎉**
