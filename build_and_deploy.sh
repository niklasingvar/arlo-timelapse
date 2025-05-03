#!/bin/bash
set -e

echo "Building Docker image..."
docker build -t arlo-lambda .

echo "Creating container to extract files..."
docker create --name arlo-temp arlo-lambda:latest
mkdir -p docker-lambda

echo "Copying Lambda package files from container..."
docker cp arlo-temp:/var/task/. docker-lambda/
docker rm arlo-temp

echo "Creating deployment package..."
cd docker-lambda
zip -r ../lambda_deployment_docker.zip .
cd ..

echo "Updating Lambda function..."
aws lambda update-function-code \
  --function-name arlo-snapshot-function \
  --zip-file fileb://lambda_deployment_docker.zip

echo "Updating Lambda function configuration..."
aws lambda update-function-configuration \
  --function-name arlo-snapshot-function \
  --handler lambda_function.lambda_handler \
  --runtime python3.12

echo "Deployment completed" 