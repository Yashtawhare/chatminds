#!/bin/bash

# SSL Setup Script for ChatMinds
# This script helps set up SSL/TLS certificates using Let's Encrypt

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <domain-name>"
    echo "Example: $0 yourdomain.com"
    exit 1
fi

DOMAIN=$1

echo "🔒 Setting up SSL for domain: $DOMAIN"

# Install certbot
echo "📦 Installing certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Stop nginx temporarily
echo "🛑 Stopping nginx temporarily..."
sudo systemctl stop nginx

# Get SSL certificate
echo "📜 Obtaining SSL certificate..."
sudo certbot certonly --standalone -d $DOMAIN

# Create SSL configuration
echo "⚙️ Creating SSL configuration..."
sudo mkdir -p /opt/chatminds/ssl

# Copy certificates to application directory
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/chatminds/ssl/
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/chatminds/ssl/
sudo chown $USER:$USER /opt/chatminds/ssl/*

# Update .env file with SSL settings
sed -i "s/SSL_ENABLED=.*/SSL_ENABLED=true/" /opt/chatminds/.env
sed -i "s/DOMAIN_NAME=.*/DOMAIN_NAME=$DOMAIN/" /opt/chatminds/.env

echo "✅ SSL certificate installed successfully!"
echo "🔄 Restarting services..."

cd /opt/chatminds
docker-compose down
docker-compose up -d

echo "🌐 Your application is now available at: https://$DOMAIN"
echo "📅 Certificate will auto-renew. To test renewal: sudo certbot renew --dry-run"