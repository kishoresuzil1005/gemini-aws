#!/bin/bash

# CloudOps AI Pipeline Deployment Script
# Run this script on your EC2 instance from the root of the gemini-aws repository.

set -e

echo "Starting deployment of CloudOps AI Context Engine..."

# 1. Pull latest code from GitHub
echo "=> Pulling latest code from GitHub (main branch)..."
git fetch origin main
git reset --hard origin/main

# 2. Restart backend using Docker Compose
echo "=> Restarting Docker containers..."
if [ -f "backend/docker-compose.yml" ]; then
    cd backend
    docker-compose down
    docker-compose up -d --build
    cd ..
elif [ -f "docker-compose.yml" ]; then
    docker-compose down
    docker-compose up -d --build
else
    echo "WARNING: Could not find docker-compose.yml. If you are not using Docker, please restart your systemd services or uvicorn processes manually."
fi

echo "=> Deployment complete!"
echo "Check logs with: cd backend && docker-compose logs -f"
