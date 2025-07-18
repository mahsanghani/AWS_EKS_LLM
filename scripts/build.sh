#!/bin/bash

set -e

echo "Building and pushing Docker image..."

# Variables
AWS_REGION=${AWS_REGION:-us-west-2}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
IMAGE_NAME=llm-api
TAG=${GITHUB_SHA:-latest}

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Build image
echo "Building Docker image..."
cd app
docker build -t $IMAGE_NAME:$TAG .

# Tag and push image
echo "Tagging and pushing image..."
docker tag $IMAGE_NAME:$TAG $ECR_REGISTRY/$IMAGE_NAME:$TAG
docker tag $IMAGE_NAME:$TAG $ECR_REGISTRY/$IMAGE_NAME:latest
docker push $ECR_REGISTRY/$IMAGE_NAME:$TAG
docker push $ECR_REGISTRY/$IMAGE_NAME:latest

echo "Image pushed successfully: $ECR_REGISTRY/$IMAGE_NAME:$TAG"
