#!/bin/bash

set -e

echo "Creating backup of Kubernetes resources..."

# Variables
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
NAMESPACE="llm-deployment"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup all resources
kubectl get all -n $NAMESPACE -o yaml > $BACKUP_DIR/all-resources.yaml
kubectl get configmaps -n $NAMESPACE -o yaml > $BACKUP_DIR/configmaps.yaml
kubectl get secrets -n $NAMESPACE -o yaml > $BACKUP_DIR/secrets.yaml
kubectl get ingress -n $NAMESPACE -o yaml > $BACKUP_DIR/ingress.yaml
kubectl get networkpolicies -n $NAMESPACE -o yaml > $BACKUP_DIR/network-policies.yaml

# Backup Terraform state
if [ -f "terraform/terraform.tfstate" ]; then
    cp terraform/terraform.tfstate $BACKUP_DIR/terraform.tfstate
fi

echo "Backup completed in $BACKUP_DIR"
