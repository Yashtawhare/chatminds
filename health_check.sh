#!/bin/bash

# Health Check Script for ChatMinds Deployment
# Usage: ./health_check.sh [domain_or_ip] [--detailed] [--json]

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DOMAIN=${1:-localhost}
DETAILED=false
JSON_OUTPUT=false
PROTOCOL="http"
LOGFILE="/tmp/chatminds_health_$(date +%Y%m%d_%H%M%S).log"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --detailed)
            DETAILED=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --https)
            PROTOCOL="https"
            shift
            ;;
        *)
            if [ -z "$DOMAIN_SET" ]; then
                DOMAIN="$1"
                DOMAIN_SET=true
            fi
            shift
            ;;
    esac
done

# Auto-detect HTTPS if SSL certificates exist
if [ -f "nginx/ssl/certificate.crt" ] && [ "$PROTOCOL" = "http" ]; then
    PROTOCOL="https"
fi

# JSON output initialization
if [ "$JSON_OUTPUT" = true ]; then
    echo '{'
    echo '  "timestamp": "'$(date -Iseconds)'",'
    echo '  "target": "'$PROTOCOL://$DOMAIN'",'
    echo '  "checks": {'
else
    echo -e "${BLUE}🔍 ChatMinds Health Check${NC}"
    echo "Target: $PROTOCOL://$DOMAIN"
    echo "Time: $(date)"
    echo "Log: $LOGFILE"
    echo "=================================="
fi

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOGFILE"
}

# JSON check result
json_result() {
    local name=$1
    local status=$2
    local details=$3
    local response_time=${4:-0}
    
    if [ "$JSON_OUTPUT" = true ]; then
        echo "    \"$name\": {"
        echo "      \"status\": \"$status\","
        echo "      \"response_time_ms\": $response_time,"
        echo "      \"details\": \"$details\""
        echo "    },"
    fi
}

# Function to check HTTP status with timing
check_endpoint() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}
    local timeout=${4:-10}
    
    log "Checking endpoint: $url"
    
    if [ "$JSON_OUTPUT" = false ]; then
        echo -n "Checking $name... "
    fi
    
    # Use curl with timing
    start_time=$(date +%s%N)
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $timeout --max-time $timeout "$url" 2>/dev/null)
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [ "$response" = "$expected_status" ]; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${GREEN}✅ OK${NC} ($response) - ${response_time}ms"
        fi
        json_result "$name" "ok" "HTTP $response" "$response_time"
        log "$name: OK ($response) - ${response_time}ms"
        return 0
    else
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${RED}❌ FAILED${NC} ($response) - ${response_time}ms"
        fi
        json_result "$name" "failed" "HTTP $response" "$response_time"
        log "$name: FAILED ($response) - ${response_time}ms"
        return 1
    fi
}

# Function to check if service is running
check_service() {
    local service=$1
    log "Checking Docker service: $service"
    
    if [ "$JSON_OUTPUT" = false ]; then
        echo -n "Checking Docker service $service... "
    fi
    
    if command -v docker-compose &> /dev/null; then
        if docker-compose ps | grep -q "$service.*Up"; then
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${GREEN}✅ Running${NC}"
            fi
            json_result "docker_$service" "running" "Container is up" 0
            log "$service: Running"
            return 0
        else
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${RED}❌ Not running${NC}"
            fi
            json_result "docker_$service" "stopped" "Container is not running" 0
            log "$service: Not running"
            return 1
        fi
    else
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${YELLOW}⚠️  Docker Compose not available${NC}"
        fi
        json_result "docker_$service" "unknown" "Docker Compose not available" 0
        log "$service: Docker Compose not available"
        return 1
    fi
}

# Function to check system resources
check_resources() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
        echo -e "${BLUE}💾 System Resources:${NC}"
        echo "-------------------"
    fi
    
    # Disk space
    if command -v df &> /dev/null; then
        disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
        disk_available=$(df -h / | awk 'NR==2 {print $4}')
        
        if [ "$JSON_OUTPUT" = false ]; then
            echo -n "Disk usage: $disk_usage% (${disk_available} available)... "
        fi
        
        if [ "$disk_usage" -lt 90 ]; then
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${GREEN}✅ OK${NC}"
            fi
            json_result "disk_usage" "ok" "${disk_usage}% used, ${disk_available} available" 0
        else
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${YELLOW}⚠️  High usage${NC}"
            fi
            json_result "disk_usage" "warning" "${disk_usage}% used, ${disk_available} available" 0
        fi
        log "Disk usage: $disk_usage% (${disk_available} available)"
    fi
    
    # Memory
    if command -v free &> /dev/null; then
        mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        mem_available=$(free -h | awk 'NR==2{print $7}')
        
        if [ "$JSON_OUTPUT" = false ]; then
            echo -n "Memory usage: $mem_usage% (${mem_available} available)... "
        fi
        
        if [ "$mem_usage" -lt 90 ]; then
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${GREEN}✅ OK${NC}"
            fi
            json_result "memory_usage" "ok" "${mem_usage}% used, ${mem_available} available" 0
        else
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${YELLOW}⚠️  High usage${NC}"
            fi
            json_result "memory_usage" "warning" "${mem_usage}% used, ${mem_available} available" 0
        fi
        log "Memory usage: $mem_usage% (${mem_available} available)"
    fi
    
    # Load average
    if command -v uptime &> /dev/null; then
        load_avg=$(uptime | awk -F'load average:' '{ print $2 }' | sed 's/^[ \t]*//')
        if [ "$JSON_OUTPUT" = false ]; then
            echo "Load average: $load_avg"
        fi
        json_result "load_average" "info" "$load_avg" 0
        log "Load average: $load_avg"
    fi
}

# Function to check SSL certificate
check_ssl() {
    if [ "$PROTOCOL" = "https" ]; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo ""
            echo -e "${BLUE}🔒 SSL Certificate:${NC}"
            echo "-------------------"
            echo -n "Checking SSL certificate... "
        fi
        
        ssl_info=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates -subject 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            expiry_date=$(echo "$ssl_info" | grep "notAfter" | cut -d= -f2)
            expiry_timestamp=$(date -d "$expiry_date" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s 2>/dev/null)
            current_timestamp=$(date +%s)
            days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
            
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${GREEN}✅ Valid${NC}"
                if [ "$DETAILED" = true ]; then
                    echo "$ssl_info"
                fi
                echo "Expires in $days_until_expiry days"
            fi
            
            if [ "$days_until_expiry" -lt 30 ]; then
                json_result "ssl_certificate" "warning" "Valid but expires in $days_until_expiry days" 0
            else
                json_result "ssl_certificate" "ok" "Valid, expires in $days_until_expiry days" 0
            fi
            log "SSL certificate: Valid, expires in $days_until_expiry days"
        else
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${RED}❌ Invalid or not found${NC}"
            fi
            json_result "ssl_certificate" "failed" "Invalid or not found" 0
            log "SSL certificate: Invalid or not found"
        fi
    fi
}

# Function to check Docker container stats
check_docker_stats() {
    if command -v docker &> /dev/null && [ "$DETAILED" = true ]; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo ""
            echo -e "${BLUE}� Container Resources:${NC}"
            echo "---------------------"
        fi
        
        for service in chatminds-web chatminds-llm nginx; do
            container_id=$(docker-compose ps -q $service 2>/dev/null)
            if [ ! -z "$container_id" ]; then
                stats=$(docker stats --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" $container_id 2>/dev/null | tail -n 1)
                if [ "$JSON_OUTPUT" = false ] && [ ! -z "$stats" ]; then
                    echo "$service: $stats"
                fi
                log "$service container stats: $stats"
            fi
        done
    fi
}

# Function to analyze logs
check_logs() {
    if [ -f "docker-compose.yml" ] && [ "$DETAILED" = true ]; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo ""
            echo -e "${BLUE}📝 Log Analysis:${NC}"
            echo "----------------"
        fi
        
        # Check for recent errors
        error_count=$(docker-compose logs --since="1h" 2>/dev/null | grep -i "error\|exception\|failed\|critical" | wc -l)
        warning_count=$(docker-compose logs --since="1h" 2>/dev/null | grep -i "warning\|warn" | wc -l)
        
        if [ "$JSON_OUTPUT" = false ]; then
            if [ "$error_count" -eq 0 ]; then
                echo -e "${GREEN}✅ No recent errors found${NC}"
            else
                echo -e "${YELLOW}⚠️  Found $error_count recent errors${NC}"
            fi
            
            if [ "$warning_count" -gt 0 ]; then
                echo -e "${YELLOW}⚠️  Found $warning_count recent warnings${NC}"
            fi
        fi
        
        json_result "recent_errors" "info" "$error_count errors, $warning_count warnings in last hour" 0
        log "Log analysis: $error_count errors, $warning_count warnings in last hour"
    fi
}

# Main health checks
if [ "$JSON_OUTPUT" = false ]; then
    echo ""
fi

# Check if we're on the server (has docker-compose)
if [ -f "docker-compose.yml" ]; then
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${BLUE}� Docker Services Status:${NC}"
        echo "-------------------------"
    fi
    check_service "chatminds-web"
    check_service "chatminds-llm" 
    check_service "nginx"
    
    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
    fi
fi

# Check web endpoints
if [ "$JSON_OUTPUT" = false ]; then
    echo -e "${BLUE}🌐 Web Endpoints:${NC}"
    echo "-----------------"
fi

check_endpoint "$PROTOCOL://$DOMAIN/" "main_application"
check_endpoint "$PROTOCOL://$DOMAIN/login" "login_page"

# Try to check a health endpoint if it exists
check_endpoint "$PROTOCOL://$DOMAIN/health" "health_endpoint" 200

# Check API endpoints
if [ "$JSON_OUTPUT" = false ]; then
    echo ""
    echo -e "${BLUE}🚀 API Endpoints:${NC}"
    echo "-----------------"
fi

if [ "$DOMAIN" = "localhost" ]; then
    # Direct API check for localhost
    check_endpoint "http://localhost:8000/docs" "llm_api_docs"
    check_endpoint "http://localhost:8000/health" "llm_health_endpoint"
else
    # Through nginx proxy
    check_endpoint "$PROTOCOL://$DOMAIN/api/llm/docs" "llm_api_docs"
    check_endpoint "$PROTOCOL://$DOMAIN/api/llm/health" "llm_health_endpoint"
fi

# Additional checks
check_ssl
check_resources
check_docker_stats
check_logs

# Summary
if [ "$JSON_OUTPUT" = true ]; then
    # Remove trailing comma and close JSON
    echo '    "completed": true'
    echo '  },'
    echo '  "summary": {'
    echo '    "timestamp": "'$(date -Iseconds)'",'
    echo '    "logfile": "'$LOGFILE'"'  
    echo '  }'
    echo '}'
else
    echo ""
    echo "=================================="
    echo -e "${GREEN}✅ Health check completed!${NC}"
    echo ""
    echo -e "${BLUE}📋 Quick Commands:${NC}"
    echo "- View logs: docker-compose logs -f"
    echo "- Restart all: docker-compose restart"
    echo "- Check status: docker-compose ps"
    echo "- Update app: git pull && docker-compose build && docker-compose up -d"
    echo "- Detailed check: ./health_check.sh $DOMAIN --detailed"
    echo "- JSON output: ./health_check.sh $DOMAIN --json"
    echo ""
    echo "📊 Log file: $LOGFILE"
fi

log "Health check completed"