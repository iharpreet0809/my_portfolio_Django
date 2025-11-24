#!/bin/bash
# Cleanup script - removes all resources

set -e

echo "⚠️  WARNING: This will delete all resources in the portfolio namespace!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo "🧹 Cleaning up all resources..."

# Delete all resources in namespace
kubectl delete all --all -n portfolio

# Delete PVCs
kubectl delete pvc --all -n portfolio

# Delete ConfigMaps and Secrets
kubectl delete configmap --all -n portfolio
kubectl delete secret --all -n portfolio

# Delete CronJobs
kubectl delete cronjob --all -n portfolio

# Optionally delete namespace
read -p "Delete namespace too? (yes/no): " delete_ns
if [ "$delete_ns" = "yes" ]; then
    kubectl delete namespace portfolio
    echo "✅ Namespace deleted."
fi

echo "✅ Cleanup complete!"
