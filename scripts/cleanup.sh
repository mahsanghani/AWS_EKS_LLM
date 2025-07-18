#!/bin/bash

set -e

echo "Cleaning up resources..."

# Variables
CLUSTER_NAME=${CLUSTER_NAME:-llm-cluster}
AWS_REGION=${AWS_REGION:-us-west-2}

# Delete Kubernetes resources
echo "Deleting Kubernetes resources..."
kubectl delete namespace llm-deployment --ignore-not-found=true

# Delete Terraform resources
echo "Destroying Terraform infrastructure..."
cd terraform
terraform destroy -auto-approve

# Delete ECR images (optional)
echo "Deleting ECR images..."
aws ecr batch-delete-image \
    --repository-name llm-api \
    --image-ids imageTag=latest \
    --region $AWS_REGION || true

# Delete IAM policies
echo "Deleting IAM policies..."
aws iam delete-policy \
    --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/AWSLoadBalancerControllerIAMPolicy \
    --region $AWS_REGION || true

echo "Cleanup completed!"
