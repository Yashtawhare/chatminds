#!/bin/bash

# Local Development Test Script for ChatMinds
echo "🚀 Starting ChatMinds local development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env file exists and has OpenAI key
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Creating one..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your OpenAI API key"
    exit 1
fi

# Check if OpenAI key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  Please update your OpenAI API key in .env file"
    echo "Current .env content:"
    cat .env
    echo ""
    echo "Replace 'your_openai_api_key_here' with your actual OpenAI API key"
    exit 1
fi

# Create necessary directories
mkdir -p chatminds/data
mkdir -p chatminds-llm/data

echo "🏗️ Building and starting services..."

# Stop any existing containers
docker-compose -f docker-compose.dev.yml down

# Build and start services
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Check service status
echo "📊 Service Status:"
docker-compose -f docker-compose.dev.yml ps

# Test endpoints
echo ""
echo "🧪 Testing endpoints..."

# Test Flask app
echo -n "Testing Flask app (http://localhost:5000)... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200\|302"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Test LLM API
echo -n "Testing LLM API (http://localhost:8000/docs)... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo ""
echo "🎉 Local development environment is ready!"
echo ""
echo "📱 Access URLs:"
echo "   Web App: http://localhost:5000"
echo "   LLM API Docs: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.dev.yml down"
echo "   Restart: docker-compose -f docker-compose.dev.yml restart"
echo ""
echo "👤 To create admin user, visit: http://localhost:5000/seed"