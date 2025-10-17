#!/bin/bash

# Digital Ocean Deployment Script for ChatMinds
# Run this script on your Digital Ocean droplet
# Usage: ./deploy.sh [--domain yourdomain.com] [--openai-key sk-xxx] [--skip-ssl]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
DOMAIN=""
OPENAI_KEY=""
SKIP_SSL=false
APP_DIR="/opt/chatminds"
LOG_FILE="/var/log/chatminds-deploy.log"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --domain)
      DOMAIN="$2"
      shift 2
      ;;
    --openai-key)
      OPENAI_KEY="$2"
      shift 2
      ;;
    --skip-ssl)
      SKIP_SSL=true
      shift
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Start deployment
log "🚀 Starting ChatMinds deployment on Digital Ocean..."

# Create log file
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo touch "$LOG_FILE"
sudo chown $USER:$USER "$LOG_FILE"

# System checks
log "🔍 Performing system checks..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   warning "This script should not be run as root for security reasons"
   read -p "Continue anyway? (y/N): " -n 1 -r
   echo
   if [[ ! $REPLY =~ ^[Yy]$ ]]; then
       exit 1
   fi
fi

# Check system resources
MEMORY_GB=$(free -g | awk 'NR==2{printf "%.1f", $2}')
if (( $(echo "$MEMORY_GB < 1.5" | bc -l) )); then
    warning "Low memory detected: ${MEMORY_GB}GB. Minimum 2GB recommended"
fi

DISK_GB=$(df -BG / | awk 'NR==2{gsub(/G/,"",$4); print $4}')
if (( DISK_GB < 10 )); then
    warning "Low disk space: ${DISK_GB}GB. Minimum 20GB recommended"
fi

# Update system packages
log "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
log "📦 Installing required packages..."
sudo apt install -y curl wget git ufw htop nano bc

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    log "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    # Enable Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
else
    log "✅ Docker already installed"
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    log "📦 Installing Docker Compose..."
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    log "✅ Docker Compose already installed"
fi

# Verify Docker installation
if ! docker --version; then
    error "Docker installation failed"
fi

if ! docker-compose --version; then
    error "Docker Compose installation failed"
fi

# Create application directory
log "📁 Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    log "🔄 Updating existing repository..."
    cd $APP_DIR
    git stash push -m "Pre-deployment stash $(date)"
    git pull origin main || error "Failed to pull latest changes"
else
    log "📥 Cloning repository..."
    git clone https://github.com/Yashtawhare/chatminds.git $APP_DIR || error "Failed to clone repository"
    cd $APP_DIR
fi

# Create .env file
log "⚙️ Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ ! -f ".env.example" ]; then
        log "Creating .env.example template..."
        cat > .env.example << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your_super_secret_key_change_this

# Database
DATABASE_URL=sqlite:///app/askai.db

# Application Settings
APP_NAME=ChatMinds
APP_VERSION=1.0.0

# Domain Configuration (for SSL)
DOMAIN=your-domain.com

# Security
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true

# API Configuration
LLM_SERVICE_URL=http://chatminds-llm:8000
WEB_SERVICE_URL=http://chatminds-web:5000

# File Upload Limits
MAX_CONTENT_LENGTH=100MB
UPLOAD_FOLDER=/app/data/uploads
EOF
    fi
    
    cp .env.example .env
    
    # Update .env with provided values
    if [ ! -z "$OPENAI_KEY" ]; then
        sed -i "s/your_openai_api_key_here/$OPENAI_KEY/" .env
        log "✅ OpenAI API key configured"
    fi
    
    if [ ! -z "$DOMAIN" ]; then
        sed -i "s/your-domain.com/$DOMAIN/" .env
        log "✅ Domain configured: $DOMAIN"
    fi
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your_super_secret_key_change_this/$SECRET_KEY/" .env
    
    if [ -z "$OPENAI_KEY" ] || [ -z "$DOMAIN" ]; then
        warning "Please edit .env file with your actual values:"
        [ -z "$OPENAI_KEY" ] && echo "   - Add your OpenAI API key"
        [ -z "$DOMAIN" ] && echo "   - Update domain name"
        read -p "Edit .env now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            nano .env
        fi
    fi
else
    log "✅ .env file already exists"
fi

# Update nginx configuration with domain
if [ ! -z "$DOMAIN" ]; then
    log "🌐 Updating nginx configuration with domain: $DOMAIN"
    sed -i "s/your-domain.com/$DOMAIN/g" nginx/nginx.conf
fi

# Create necessary directories
log "📁 Creating necessary directories..."
mkdir -p chatminds/data
mkdir -p chatminds-llm/data
mkdir -p nginx/ssl
mkdir -p backups
mkdir -p logs

# Set proper permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh health_check.sh validate_env.sh 2>/dev/null || true

# Validate environment
if [ -f "validate_env.sh" ]; then
    log "🔍 Validating environment configuration..."
    ./validate_env.sh || warning "Environment validation had warnings"
fi

# Build and start services
log "🏗️ Building and starting services..."
docker-compose down --remove-orphans 2>/dev/null || true

# Clean up old images to save space
docker system prune -f || true

log "Building Docker images..."
docker-compose build --no-cache || error "Failed to build Docker images"

log "Starting services..."
docker-compose up -d || error "Failed to start services"

# Wait for services to start and perform health checks
log "⏳ Waiting for services to start..."
sleep 30

# Health check function
check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s --max-time 10 "$url" > /dev/null 2>&1; then
            log "✅ $service is healthy"
            return 0
        fi
        info "Attempt $attempt/$max_attempts: Waiting for $service..."
        sleep 10
        ((attempt++))
    done
    
    error "$service failed to start properly"
}

# Perform health checks
log "🏥 Performing health checks..."
check_service "Web Application" "http://localhost:5000"
check_service "LLM Service" "http://localhost:8000"

# Check service status
log "✅ Checking service status..."
docker-compose ps

# Setup firewall
log "🔥 Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw --force enable

# SSL setup
if [ "$SKIP_SSL" = false ] && [ ! -z "$DOMAIN" ]; then
    log "🔒 Setting up SSL certificates..."
    if command -v certbot &> /dev/null; then
        # Stop nginx temporarily
        docker-compose stop nginx
        
        # Get SSL certificate
        sudo certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" || warning "SSL certificate generation failed"
        
        # Copy certificates if they exist
        if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
            sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ./nginx/ssl/certificate.crt
            sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ./nginx/ssl/private.key
            sudo chown $USER:$USER ./nginx/ssl/*
            
            # Update nginx config to enable SSL
            sed -i 's/# ssl_certificate/ssl_certificate/g' nginx/nginx.conf
            sed -i 's/# ssl_certificate_key/ssl_certificate_key/g' nginx/nginx.conf
            sed -i 's/# ssl_protocols/ssl_protocols/g' nginx/nginx.conf
            sed -i 's/# ssl_ciphers/ssl_ciphers/g' nginx/nginx.conf
            sed -i 's/listen 80;/#listen 80;/g' nginx/nginx.conf
            
            log "✅ SSL certificates installed"
        fi
        
        # Restart nginx
        docker-compose start nginx
    else
        warning "Certbot not installed. Run 'sudo snap install --classic certbot' to enable SSL"
    fi
fi

# Create backup script
log "💾 Setting up backup system..."
cat > backup_chatminds.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/chatminds/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup database
docker-compose exec -T chatminds-web cp /app/askai.db "/app/data/askai_backup_$DATE.db"

# Backup configuration
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" .env nginx/nginx.conf docker-compose.yml

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*backup_*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*backup_*.db" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup_chatminds.sh

# Setup log rotation
log "📊 Setting up log rotation..."
sudo tee /etc/logrotate.d/chatminds > /dev/null << EOF
$LOG_FILE {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
}
EOF

# Final checks
log "� Final system checks..."
if curl -f -s "http://localhost" > /dev/null; then
    log "✅ Application is accessible locally"
else
    warning "Application may not be fully ready yet"
fi

# Create systemd service for auto-start
log "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/chatminds.service > /dev/null << EOF
[Unit]
Description=ChatMinds Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable chatminds.service

log "🎉 Deployment complete!"
echo ""
log "�📝 Next steps:"
echo "1. Update your domain's DNS to point to this server's IP: $(curl -s ifconfig.me)"
[ -z "$DOMAIN" ] && echo "2. Set up your domain name in .env and nginx/nginx.conf"
[ "$SKIP_SSL" = true ] && echo "3. Set up SSL certificates for production (see SSL_SETUP.md)"
echo "4. Access your application at: http://$([ ! -z "$DOMAIN" ] && echo "$DOMAIN" || echo "$(curl -s ifconfig.me)")"
echo "5. Create admin account on first visit"
echo ""
log "📊 Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Restart services: docker-compose restart"
echo "- Stop services: docker-compose down"
echo "- Update application: git pull && docker-compose build && docker-compose up -d"
echo "- Run backup: ./backup_chatminds.sh"
echo "- Check health: ./health_check.sh"
echo ""
log "📋 Service URLs:"
echo "- Web Interface: http://$([ ! -z "$DOMAIN" ] && echo "$DOMAIN" || echo "localhost")"
echo "- LLM API: http://$([ ! -z "$DOMAIN" ] && echo "$DOMAIN" || echo "localhost")/api/llm/"
echo "- Logs: tail -f $LOG_FILE"