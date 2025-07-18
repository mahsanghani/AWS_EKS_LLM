#!/bin/bash

set -e

echo "Deploying to EKS..."

# Variables
AWS_REGION=${AWS_REGION:-us-west-2}
CLUSTER_NAME=${CLUSTER_NAME:-llm-cluster}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
IMAGE_TAG=${GITHUB_SHA:-latest}

# Update kubeconfig
aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME

# Update image in deployment
echo "Updating deployment with new image..."
sed -i "s|your-account.dkr.ecr.us-west-2.amazonaws.com/llm-api:latest|$ECR_REGISTRY/llm-api:$IMAGE_TAG|g" k8s/deployment.yaml

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/llm-deployment -n llm-deployment --timeout=300s

# Get service endpoints
echo "Getting service information..."
kubectl get services -n llm-deployment
kubectl get ingress -n llm-deployment

echo "Deployment complete!"
