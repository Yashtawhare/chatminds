#!/bin/bash

# Health Check Script for ChatMinds Deployment
# Usage: ./health_check.sh [domain_or_ip]

DOMAIN=${1:-localhost}
PROTOCOL="http"

echo "🔍 Checking ChatMinds deployment health..."
echo "Target: $PROTOCOL://$DOMAIN"
echo "=================================="

# Function to check HTTP status
check_endpoint() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        echo "✅ OK ($response)"
        return 0
    else
        echo "❌ FAILED ($response)"
        return 1
    fi
}

# Function to check if service is running
check_service() {
    local service=$1
    echo -n "Checking Docker service $service... "
    
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✅ Running"
        return 0
    else
        echo "❌ Not running"
        return 1
    fi
}

# Check if we're on the server (has docker-compose)
if [ -f "docker-compose.yml" ]; then
    echo "📊 Docker Services Status:"
    echo "-------------------------"
    check_service "chatminds-web"
    check_service "chatminds-llm" 
    check_service "nginx"
    echo ""
fi

# Check web endpoints
echo "🌐 Web Endpoints:"
echo "-----------------"
check_endpoint "$PROTOCOL://$DOMAIN/" "Main Application"
check_endpoint "$PROTOCOL://$DOMAIN/login" "Login Page"

# Check API endpoints
echo ""
echo "🚀 API Endpoints:"
echo "-----------------"
if [ "$DOMAIN" = "localhost" ]; then
    # Direct API check for localhost
    check_endpoint "http://localhost:8000/docs" "LLM API Docs"
else
    # Through nginx proxy
    check_endpoint "$PROTOCOL://$DOMAIN/api/llm/docs" "LLM API Docs"
fi

# Check SSL if HTTPS
if [ "$PROTOCOL" = "https" ]; then
    echo ""
    echo "🔒 SSL Certificate:"
    echo "-------------------"
    echo -n "Checking SSL certificate... "
    
    ssl_info=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "✅ Valid"
        echo "$ssl_info"
    else
        echo "❌ Invalid or not found"
    fi
fi

# Check disk space and memory (if on server)
if command -v df &> /dev/null && command -v free &> /dev/null; then
    echo ""
    echo "💾 System Resources:"
    echo "-------------------"
    
    # Disk space
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    echo -n "Disk usage: $disk_usage%... "
    if [ "$disk_usage" -lt 90 ]; then
        echo "✅ OK"
    else
        echo "⚠️  High usage"
    fi
    
    # Memory
    mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    echo -n "Memory usage: $mem_usage%... "
    if [ "$mem_usage" -lt 90 ]; then
        echo "✅ OK"
    else
        echo "⚠️  High usage"
    fi
fi

# Check logs for errors (if on server)
if [ -f "docker-compose.yml" ]; then
    echo ""
    echo "📝 Recent Errors in Logs:"
    echo "-------------------------"
    
    error_count=$(docker-compose logs --since="1h" 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)
    
    if [ "$error_count" -eq 0 ]; then
        echo "✅ No recent errors found"
    else
        echo "⚠️  Found $error_count recent errors"
        echo "View detailed logs with: docker-compose logs -f"
    fi
fi

echo ""
echo "=================================="
echo "Health check completed!"
echo ""
echo "📋 Quick Commands:"
echo "- View logs: docker-compose logs -f"
echo "- Restart all: docker-compose restart"
echo "- Check status: docker-compose ps"
echo "- Update app: git pull && docker-compose build && docker-compose up -d"