#!/bin/bash

# DigitalOcean Droplet Setup Script for ChatMinds
# Run this script on a fresh Ubuntu 22.04 droplet

set -e

echo "🚀 Starting ChatMinds deployment setup on DigitalOcean..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing required packages..."
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    ufw \
    fail2ban \
    nginx \
    git

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -aG docker $USER

# Configure UFW firewall
echo "🔒 Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Configure fail2ban
echo "🛡️ Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/chatminds
sudo chown $USER:$USER /opt/chatminds

# Clone repository (if not already present)
if [ ! -d "/opt/chatminds/.git" ]; then
    echo "📥 Cloning ChatMinds repository..."
    git clone https://github.com/Yashtawhare/chatminds.git /opt/chatminds
else
    echo "📥 Updating ChatMinds repository..."
    cd /opt/chatminds
    git pull origin main
fi

cd /opt/chatminds

# Copy environment file
echo "⚙️ Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.production .env
    echo "❗ IMPORTANT: Edit the .env file with your actual configuration values!"
    echo "   - Set your OPENAI_API_KEY"
    echo "   - Set your FLASK_SECRET_KEY" 
    echo "   - Set your DOMAIN_NAME"
fi

# Create nginx directories
echo "🌐 Setting up nginx directories..."
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled
sudo mkdir -p /opt/chatminds/nginx
sudo mkdir -p /opt/chatminds/ssl

echo "✅ Server setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /opt/chatminds/.env with your actual configuration"
echo "2. Run the deployment script: ./deploy/deploy.sh"
echo "3. Set up SSL certificates (optional but recommended)"
echo ""
echo "💡 To complete setup, run: newgrp docker && cd /opt/chatminds && ./deploy/deploy.sh"