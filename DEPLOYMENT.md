# ChatMinds - Digital Ocean Deployment Guide

This guide will help you deploy the ChatMinds application (Flask web app + FastAPI LLM service) on Digital Ocean using Docker.

## 🏗️ Architecture

- **chatminds**: Flask web application (Port 5000)
- **chatminds-llm**: FastAPI LLM service (Port 8000)  
- **nginx**: Reverse proxy and load balancer (Ports 80/443)

## 📋 Prerequisites

1. **Digital Ocean Droplet**
   - Minimum: 2GB RAM, 1 vCPU, 25GB SSD
   - Recommended: 4GB RAM, 2 vCPUs, 50GB SSD
   - Ubuntu 20.04/22.04 LTS

2. **Domain Name** (optional)
   - Point your domain to your droplet's IP address

3. **OpenAI API Key**
   - Required for LLM functionality

## 🚀 Quick Deployment

### 1. Connect to Your Droplet
```bash
ssh root@your-droplet-ip
```

### 2. Run the Deployment Script
```bash
curl -fsSL https://raw.githubusercontent.com/Yashtawhare/chatminds/main/deploy.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Install Docker and Docker Compose
- Clone your repository
- Set up environment variables
- Build and start all services
- Configure firewall

### 3. Configure Environment Variables
Edit the `.env` file with your actual values:
```bash
nano /opt/chatminds/.env
```

Update:
- `OPENAI_API_KEY=your_actual_openai_api_key`
- Domain name in `nginx/nginx.conf`

### 4. Restart Services
```bash
cd /opt/chatminds
docker-compose restart
```

## 🔧 Manual Deployment

If you prefer manual setup:

### 1. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
```

### 2. Clone Repository
```bash
ssh root@your-droplet-ip
git clone https://github.com/Yashtawhare/chatminds.git /opt/chatminds
cd /opt/chatminds
```

### 3. Configure Environment
```bash
cp .env.example .env
nano .env  # Add your OpenAI API key
```

### 4. Update Domain Configuration
```bash
nano nginx/nginx.conf  # Replace 'your-domain.com' with your actual domain
```

### 5. Build and Start Services
```bash
docker-compose build
docker-compose up -d
```

## 🔐 SSL Certificate Setup

For HTTPS (recommended for production):

### Option 1: Let's Encrypt (Free)
```bash
# Install Certbot
sudo snap install --classic certbot

# Stop nginx temporarily
docker-compose stop nginx

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/certificate.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/private.key

# Update nginx config (uncomment SSL lines)
nano nginx/nginx.conf

# Restart services
docker-compose up -d
```

See `SSL_SETUP.md` for detailed SSL configuration.

## 🎯 Access Your Application

- **Web Interface**: `http://your-domain.com` or `http://your-droplet-ip`
- **LLM API**: `http://your-domain.com/api/llm/` or `http://your-droplet-ip:8000`

### Default Admin Account
On first run, create an admin account:
1. Visit `/seed` to create the admin user
2. Login with:
   - Username: `admin`
   - Password: `admin`
   - Change these credentials immediately!

## 📊 Management Commands

### View Service Status
```bash
cd /opt/chatminds
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f chatminds-web
docker-compose logs -f chatminds-llm
docker-compose logs -f nginx
```

### Restart Services
```bash
docker-compose restart
# or specific service
docker-compose restart chatminds-web
```

### Update Application
```bash
cd /opt/chatminds
git pull origin main
docker-compose build
docker-compose up -d
```

### Backup Database
```bash
# Create backup
docker-compose exec chatminds-web cp /app/askai.db /app/data/askai_backup_$(date +%Y%m%d_%H%M%S).db

# Copy to host
docker cp $(docker-compose ps -q chatminds-web):/app/data/ ./backups/
```

### Stop Services
```bash
docker-compose down
```

## 🔥 Firewall Configuration

The deployment script automatically configures UFW:
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Database Issues
```bash
# Access Flask container
docker-compose exec chatminds-web bash

# Initialize database
python -c "from app import create_tables; create_tables()"
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/chatminds

# Fix permissions
chmod +x deploy.sh
```

### OpenAI API Issues
- Verify your API key in `.env`
- Check API quota and billing
- View LLM service logs: `docker-compose logs chatminds-llm`

## 🔧 Configuration Files

- `docker-compose.yml`: Multi-container setup
- `nginx/nginx.conf`: Reverse proxy configuration
- `.env`: Environment variables
- `chatminds/Dockerfile`: Flask app container
- `chatminds-llm/Dockerfile`: FastAPI service container

## 📈 Scaling and Performance

### For Higher Traffic:
1. **Upgrade Droplet**: More CPU/RAM
2. **Database**: Consider PostgreSQL instead of SQLite
3. **Load Balancing**: Multiple app instances
4. **CDN**: CloudFlare or DigitalOcean Spaces

### Performance Monitoring:
```bash
# System resources
htop
df -h

# Docker stats
docker stats

# Service health
curl -I http://localhost
curl -I http://localhost:8000
```

## 🔄 Updates and Maintenance

### Regular Maintenance:
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Clean up old images
docker system prune -a
```

### Monitoring Logs:
Set up log rotation and monitoring for production use:
```bash
# Add to crontab
0 0 * * 0 docker system prune -f
```

## 🆘 Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify configuration files
3. Test individual services
4. Check firewall settings
5. Verify DNS configuration (if using domain)

---

**Note**: Replace `your-domain.com` and `your-droplet-ip` with your actual values throughout the setup.