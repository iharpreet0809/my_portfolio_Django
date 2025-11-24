#!/bin/bash
# Initial SSL Certificate Setup for iharpreet.com

set -e

echo "🔒 Setting up SSL certificates for iharpreet.com..."

# Run certbot to obtain initial certificates
kubectl run certbot-init \
  --image=certbot/certbot \
  --restart=Never \
  --namespace=portfolio \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "certbot",
      "image": "certbot/certbot",
      "command": [
        "certbot",
        "certonly",
        "--webroot",
        "--webroot-path=/var/www/certbot",
        "--email", "talkwithharpreet@gmail.com",
        "--agree-tos",
        "--no-eff-email",
        "--non-interactive",
        "--keep-until-expiring",
        "-d", "iharpreet.com",
        "-d", "www.iharpreet.com"
      ],
      "volumeMounts": [
        {
          "name": "certbot-www",
          "mountPath": "/var/www/certbot"
        },
        {
          "name": "certbot-conf",
          "mountPath": "/etc/letsencrypt"
        }
      ]
    }],
    "volumes": [
      {
        "name": "certbot-www",
        "persistentVolumeClaim": {
          "claimName": "certbot-www-pvc"
        }
      },
      {
        "name": "certbot-conf",
        "persistentVolumeClaim": {
          "claimName": "certbot-conf-pvc"
        }
      }
    ]
  }
}'

echo "⏳ Waiting for certificate generation..."
kubectl wait --for=condition=complete --timeout=300s pod/certbot-init -n portfolio

echo "📋 Certificate generation logs:"
kubectl logs certbot-init -n portfolio

echo "🧹 Cleaning up init pod..."
kubectl delete pod certbot-init -n portfolio

echo ""
echo "✅ SSL certificates obtained!"
echo "🔄 Restarting Nginx to load certificates..."
kubectl rollout restart deployment/nginx -n portfolio

echo ""
echo "✅ Setup complete! Your site should now be accessible via HTTPS."
