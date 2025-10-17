#!/bin/bash

# Monitoring and Alerting Script for ChatMinds
# Usage: ./monitoring.sh [--setup] [--alert-email your@email.com] [--alert-webhook https://hooks.slack.com/...]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_LOG="/var/log/chatminds-monitor.log"
PID_FILE="/tmp/chatminds-monitor.pid" 
CONFIG_FILE="$SCRIPT_DIR/monitor.conf"
ALERT_EMAIL=""
ALERT_WEBHOOK=""
CHECK_INTERVAL=300  # 5 minutes
DOMAIN="localhost"

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90
RESPONSE_TIME_THRESHOLD=5000  # 5 seconds
ERROR_RATE_THRESHOLD=10

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load configuration if exists
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --setup)
            SETUP_MODE=true
            shift
            ;;
        --alert-email)
            ALERT_EMAIL="$2"
            shift 2
            ;;
        --alert-webhook)
            ALERT_WEBHOOK="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --daemon)
            DAEMON_MODE=true
            shift
            ;;
        --stop)
            STOP_DAEMON=true
            shift
            ;;
        --status)
            STATUS_CHECK=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$MONITOR_LOG"
}

# Alert function
send_alert() {
    local subject="$1"
    local message="$2"
    local severity="${3:-WARNING}"
    
    log "ALERT [$severity]: $subject - $message"
    
    # Email alert
    if [ ! -z "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "ChatMinds Alert: $subject" "$ALERT_EMAIL"
    fi
    
    # Webhook alert (Slack, Discord, etc.)
    if [ ! -z "$ALERT_WEBHOOK" ]; then
        curl -s -X POST "$ALERT_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"🚨 ChatMinds Alert: $subject\n$message\"}" || true
    fi
    
    # System notification if available
    if command -v notify-send &> /dev/null; then
        notify-send "ChatMinds Alert" "$subject: $message"
    fi
}

# Setup monitoring
setup_monitoring() {
    log "Setting up ChatMinds monitoring..."
    
    # Create configuration file
    cat > "$CONFIG_FILE" << EOF
# ChatMinds Monitoring Configuration
DOMAIN="$DOMAIN"
ALERT_EMAIL="$ALERT_EMAIL"
ALERT_WEBHOOK="$ALERT_WEBHOOK"
CHECK_INTERVAL=$CHECK_INTERVAL
CPU_THRESHOLD=$CPU_THRESHOLD
MEMORY_THRESHOLD=$MEMORY_THRESHOLD
DISK_THRESHOLD=$DISK_THRESHOLD
RESPONSE_TIME_THRESHOLD=$RESPONSE_TIME_THRESHOLD
ERROR_RATE_THRESHOLD=$ERROR_RATE_THRESHOLD
EOF
    
    # Setup log rotation
    if command -v logrotate &> /dev/null; then
        sudo tee /etc/logrotate.d/chatminds-monitor > /dev/null << EOF
$MONITOR_LOG {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
}
EOF
        log "Log rotation configured"
    fi
    
    # Create systemd service
    sudo tee /etc/systemd/system/chatminds-monitor.service > /dev/null << EOF
[Unit]
Description=ChatMinds Monitoring Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/monitoring.sh --daemon
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable chatminds-monitor.service
    
    log "Monitoring setup completed!"
    echo "To start monitoring: sudo systemctl start chatminds-monitor"
    echo "To check status: sudo systemctl status chatminds-monitor"
}

# Stop daemon
stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$PID_FILE"
            log "Monitoring daemon stopped"
        else
            log "Monitoring daemon was not running"
            rm -f "$PID_FILE"
        fi
    else
        log "No PID file found"
    fi
    
    # Also stop systemd service if running
    if systemctl is-active --quiet chatminds-monitor 2>/dev/null; then
        sudo systemctl stop chatminds-monitor
        log "Systemd service stopped"
    fi
}

# Check daemon status
check_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✅ Monitoring daemon is running (PID: $pid)${NC}"
        else
            echo -e "${RED}❌ PID file exists but process is not running${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️  Monitoring daemon is not running${NC}"
    fi
    
    # Check systemd service
    if systemctl is-active --quiet chatminds-monitor 2>/dev/null; then
        echo -e "${GREEN}✅ Systemd service is active${NC}"
    else
        echo -e "${YELLOW}⚠️  Systemd service is inactive${NC}"
    fi
}

# Check system metrics
check_system_metrics() {
    local alerts=()
    
    # CPU usage
    if command -v top &> /dev/null; then
        local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
        if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
            alerts+=("High CPU usage: ${cpu_usage}%")
        fi
    fi
    
    # Memory usage
    if command -v free &> /dev/null; then
        local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [ "$mem_usage" -gt "$MEMORY_THRESHOLD" ]; then
            alerts+=("High memory usage: ${mem_usage}%")
        fi
    fi
    
    # Disk usage
    if command -v df &> /dev/null; then
        local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
        if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
            alerts+=("High disk usage: ${disk_usage}%")
        fi
    fi
    
    # Docker container health
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        local containers_down=()
        for service in chatminds-web chatminds-llm nginx; do
            if ! docker-compose ps | grep -q "$service.*Up"; then
                containers_down+=("$service")
            fi
        done
        
        if [ ${#containers_down[@]} -gt 0 ]; then
            alerts+=("Services down: ${containers_down[*]}")
        fi
    fi
    
    # Send alerts if any
    for alert in "${alerts[@]}"; do
        send_alert "System Alert" "$alert" "WARNING"
    done
}

# Check application health
check_application_health() {
    local alerts=()
    local protocol="http"
    
    # Auto-detect HTTPS
    if [ -f "nginx/ssl/certificate.crt" ]; then
        protocol="https"
    fi
    
    # Check main application
    local start_time=$(date +%s%N)
    local response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 10 "$protocol://$DOMAIN/" 2>/dev/null || echo "000")
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [ "$response" != "200" ]; then
        alerts+=("Main application not responding (HTTP $response)")
    elif [ "$response_time" -gt "$RESPONSE_TIME_THRESHOLD" ]; then
        alerts+=("Slow response time: ${response_time}ms")
    fi
    
    # Check API health
    local api_url="$protocol://$DOMAIN/api/llm/health"
    if [ "$DOMAIN" = "localhost" ]; then
        api_url="http://localhost:8000/health"
    fi
    
    local api_response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 10 "$api_url" 2>/dev/null || echo "000")
    if [ "$api_response" != "200" ]; then
        alerts+=("LLM API not responding (HTTP $api_response)")
    fi
    
    # Check for errors in logs
    if [ -f "docker-compose.yml" ]; then
        local error_count=$(docker-compose logs --since="5m" 2>/dev/null | grep -i "error\|exception\|failed\|critical" | wc -l)
        if [ "$error_count" -gt "$ERROR_RATE_THRESHOLD" ]; then
            alerts+=("High error rate: $error_count errors in last 5 minutes")
        fi
    fi
    
    # Send alerts if any
    for alert in "${alerts[@]}"; do
        send_alert "Application Alert" "$alert" "CRITICAL"
    done
}

# Check SSL certificate expiry
check_ssl_expiry() {
    if [ -f "nginx/ssl/certificate.crt" ]; then
        local expiry_date=$(openssl x509 -enddate -noout -in nginx/ssl/certificate.crt | cut -d= -f2)
        local expiry_timestamp=$(date -d "$expiry_date" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s 2>/dev/null)
        local current_timestamp=$(date +%s)
        local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
        
        if [ "$days_until_expiry" -lt 30 ]; then
            send_alert "SSL Certificate Expiry" "Certificate expires in $days_until_expiry days" "WARNING"
        elif [ "$days_until_expiry" -lt 7 ]; then
            send_alert "SSL Certificate Expiry" "Certificate expires in $days_until_expiry days - URGENT" "CRITICAL"
        fi
    fi
}

# Main monitoring loop
monitoring_loop() {
    log "Starting monitoring daemon with PID $$"
    echo $$ > "$PID_FILE"
    
    # Trap signals for graceful shutdown
    trap 'log "Received shutdown signal"; rm -f "$PID_FILE"; exit 0' SIGTERM SIGINT
    
    while true; do
        log "Running health checks..."
        
        check_system_metrics
        check_application_health
        check_ssl_expiry
        
        log "Health check completed, sleeping for $CHECK_INTERVAL seconds"
        sleep "$CHECK_INTERVAL"
    done
}

# Generate monitoring report
generate_report() {
    local report_file="/tmp/chatminds_report_$(date +%Y%m%d_%H%M%S).html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>ChatMinds Monitoring Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .ok { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ChatMinds Monitoring Report</h1>
        <p>Generated: $(date)</p>
        <p>Domain: $DOMAIN</p>
    </div>
    
    <div class="section">
        <h2>System Status</h2>
        <table>
            <tr><th>Metric</th><th>Value</th><th>Status</th></tr>
EOF
    
    # Add system metrics to report
    if command -v free &> /dev/null; then
        local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        local mem_status="ok"
        [ "$mem_usage" -gt "$MEMORY_THRESHOLD" ] && mem_status="error"
        echo "            <tr><td>Memory Usage</td><td>${mem_usage}%</td><td class=\"$mem_status\">$mem_status</td></tr>" >> "$report_file"
    fi
    
    if command -v df &> /dev/null; then
        local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
        local disk_status="ok"
        [ "$disk_usage" -gt "$DISK_THRESHOLD" ] && disk_status="error"
        echo "            <tr><td>Disk Usage</td><td>${disk_usage}%</td><td class=\"$disk_status\">$disk_status</td></tr>" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF
        </table>
    </div>
    
    <div class="section">
        <h2>Recent Logs</h2>
        <pre>$(tail -n 50 "$MONITOR_LOG" 2>/dev/null || echo "No logs available")</pre>
    </div>
</body>
</html>
EOF
    
    echo "Report generated: $report_file"
    
    # Email report if configured
    if [ ! -z "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        mail -s "ChatMinds Monitoring Report" -a "$report_file" "$ALERT_EMAIL" < /dev/null
        log "Report emailed to $ALERT_EMAIL"
    fi
}

# Main execution
main() {
    # Create log file if it doesn't exist
    sudo touch "$MONITOR_LOG" 2>/dev/null || touch "$MONITOR_LOG"
    sudo chown $USER:$USER "$MONITOR_LOG" 2>/dev/null || true
    
    if [ "$SETUP_MODE" = true ]; then
        setup_monitoring
    elif [ "$STOP_DAEMON" = true ]; then
        stop_daemon
    elif [ "$STATUS_CHECK" = true ]; then
        check_status
    elif [ "$DAEMON_MODE" = true ]; then
        monitoring_loop
    else
        echo "ChatMinds Monitoring Script"
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --setup                    Setup monitoring service"
        echo "  --daemon                   Run in daemon mode"
        echo "  --stop                     Stop monitoring daemon"
        echo "  --status                   Check daemon status"
        echo "  --domain DOMAIN           Set domain to monitor"
        echo "  --alert-email EMAIL       Set alert email"
        echo "  --alert-webhook URL       Set alert webhook URL"
        echo ""
        echo "Examples:"
        echo "  $0 --setup --domain myapp.com --alert-email admin@myapp.com"
        echo "  $0 --daemon"
        echo "  $0 --status"
        echo "  $0 --stop"
        
        # Run a one-time check
        echo ""
        echo "Running one-time health check..."
        check_system_metrics
        check_application_health
        check_ssl_expiry
        generate_report
    fi
}

# Run main function
main "$@"