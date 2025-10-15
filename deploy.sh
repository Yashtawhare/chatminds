#!/bin/bash

# Digital Ocean Deployment Script for ChatMinds
# Run this script on your Digital Ocean droplet

set -e

echo "🚀 Starting ChatMinds deployment on Digital Ocean..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install Git if not installed
if ! command -v git &> /dev/null; then
    echo "📦 Installing Git..."
    sudo apt install git -y
fi

# Create application directory
APP_DIR="/opt/chatminds"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    echo "🔄 Updating existing repository..."
    cd $APP_DIR
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/Yashtawhare/chatminds.git $APP_DIR
    cd $APP_DIR
fi

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up environment variables..."
    cp .env.example .env
    echo "❗ Please edit .env file with your actual values:"
    echo "   - Add your OpenAI API key"
    echo "   - Update domain name in nginx/nginx.conf"
    nano .env
fi

# Create necessary directories
mkdir -p chatminds/data
mkdir -p chatminds-llm/data
mkdir -p nginx/ssl

# Set proper permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "✅ Checking service status..."
docker-compose ps

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw --force enable

echo "🎉 Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update your domain's DNS to point to this server's IP address"
echo "2. Set up SSL certificates (see SSL_SETUP.md)"
echo "3. Access your application at: http://your-domain.com"
echo "4. Default admin credentials will be created on first run"
echo ""
echo "📊 Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Restart services: docker-compose restart"
echo "- Stop services: docker-compose down"
echo "- Update application: git pull && docker-compose build && docker-compose up -d"