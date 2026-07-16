#!/bin/bash
set -e

echo "🚀 Starting UsePDF deployment..."

# Pull latest changes
echo "📥 Pulling latest changes from git..."
git pull origin main

# Build and start the containers
echo "🏗️ Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

# Remove unused Docker resources to save space on the VPS
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo "✅ Deployment complete! Your application is now running in production mode."
