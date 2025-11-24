# Quick Start Guide - Deploy in 5 Minutes

Fast deployment guide for experienced users.

## Prerequisites

- Kubernetes cluster running
- kubectl configured
- Docker image: `harpreetdevops/portfolio:latest` pushed to Docker Hub

## Deployment Steps

### 1. Clone & Navigate

```bash
cd /portfolio  # or your project directory
cd k8s
```

### 2. Update Secrets

```bash
nano base/secret.yaml
```

Update these values:
- `SECRET_KEY`: Your Django secret key
- `MYSQL_PASSWORD`: Strong password
- `MYSQL_ROOT_PASSWORD`: Strong root password
- `EMAIL_HOST_PASSWORD`: Email app password

### 3. Deploy

```bash
chmod +x *.sh
./deploy.sh
```

### 4. Get LoadBalancer IP

```bash
kubectl get svc nginx -n portfolio
```

### 5. Update DNS

Point your domain to the LoadBalancer IP:
```
iharpreet.com        -> LoadBalancer IP/DNS
www.iharpreet.com    -> LoadBalancer IP/DNS
```

### 6. Wait for DNS (5-30 minutes)

```bash
# Check DNS propagation
nslookup iharpreet.com
```

### 7. Setup SSL

```bash
./certbot-init.sh
```

### 8. Verify

```bash
# Check all pods running
kubectl get pods -n portfolio

# Test site
curl -I https://iharpreet.com
```

## Done! 🎉

Your site is live at: **https://iharpreet.com**

---

## Quick Commands

```bash
# View logs
kubectl logs -f deployment/django -n portfolio

# Scale
kubectl scale deployment django --replicas=3 -n portfolio

# Update image
kubectl set image deployment/django django=harpreetdevops/portfolio:v2.0 -n portfolio

# Rollback
./rollback.sh

# Cleanup
./cleanup.sh
```

## Troubleshooting

**Pods not starting?**
```bash
kubectl describe pod <pod-name> -n portfolio
kubectl logs <pod-name> -n portfolio
```

**Database issues?**
```bash
kubectl logs mysql-0 -n portfolio
```

**SSL not working?**
```bash
./certbot-init.sh  # Run again
kubectl logs certbot-init -n portfolio
```

For detailed guide, see [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md)
