#!/bin/bash

# ChatMinds Deployment Script
# This script deploys the application using Docker Compose

set -e

cd "$(dirname "$0")/.."

echo "🚀 Deploying ChatMinds application..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.production to .env and configure it with your values."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running or not accessible."
    echo "Please ensure Docker is installed and running."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ssl logs data/backend data/frontend

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Pull latest images and rebuild
echo "🔄 Building and starting containers..."
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    
    echo "📊 Service status:"
    docker-compose ps
    
    echo ""
    echo "🌐 Application URLs:"
    echo "   Frontend: http://localhost:5000 (or your domain)"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📋 Next steps:"
    echo "1. Visit http://your-domain.com/create_tables to initialize the database"
    echo "2. Visit http://your-domain.com/seed to create admin user"
    echo "3. Login with admin/admin credentials"
    echo ""
    echo "📝 To view logs: docker-compose logs -f"
    echo "🔄 To restart: ./deploy/deploy.sh"
    echo "🛑 To stop: docker-compose down"
    
else
    echo "❌ Some services failed to start. Checking logs..."
    docker-compose logs
    exit 1
fi