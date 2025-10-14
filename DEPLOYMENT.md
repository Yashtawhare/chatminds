# ChatMinds DigitalOcean Deployment Guide

This guide will help you deploy the ChatMinds application on a DigitalOcean droplet using Docker and nginx.

## 📋 Prerequisites

- A DigitalOcean account
- A domain name (optional but recommended for SSL)
- OpenAI API key
- Basic knowledge of Linux command line

## 🚀 Quick Start

### Step 1: Create a DigitalOcean Droplet

1. **Create a new droplet:**
   - Image: Ubuntu 22.04 LTS
   - Size: Basic plan, 2GB RAM minimum (4GB+ recommended)
   - Location: Choose closest to your users
   - SSH Key: Add your SSH key for secure access

2. **Connect to your droplet:**
   ```bash
   ssh root@your-droplet-ip
   ```

### Step 2: Run the Automated Setup

1. **Download and run the setup script:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/Yashtawhare/chatminds/main/deploy/setup-server.sh | bash
   ```

   Or manually:
   ```bash
   git clone https://github.com/Yashtawhare/chatminds.git /opt/chatminds
   cd /opt/chatminds
   chmod +x deploy/*.sh
   ./deploy/setup-server.sh
   ```

2. **Configure environment variables:**
   ```bash
   cd /opt/chatminds
   nano .env
   ```

   **Required settings:**
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-api-key
   FLASK_SECRET_KEY=generate-a-secure-random-string-here
   DOMAIN_NAME=your-domain.com
   ```

   To generate a secure Flask secret key:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

### Step 3: Deploy the Application

1. **Start the application:**
   ```bash
   newgrp docker  # Refresh group membership
   ./deploy/deploy.sh
   ```

2. **Initialize the database:**
   - Visit `http://your-droplet-ip/create_tables`
   - Visit `http://your-droplet-ip/seed`

3. **Login as admin:**
   - Username: `admin`
   - Password: `admin`
   - **⚠️ Change the admin password immediately after first login**

### Step 4: Set Up SSL (Recommended)

1. **Point your domain to the droplet:**
   - Add an A record pointing your domain to the droplet's IP address

2. **Run the SSL setup script:**
   ```bash
   ./deploy/setup-ssl.sh your-domain.com
   ```

## 🔧 Manual Deployment Steps

If you prefer to set up everything manually:

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install nginx and other tools
sudo apt install -y nginx git ufw fail2ban
```

### 2. Configure Firewall

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Clone and Configure

```bash
# Clone repository
git clone https://github.com/Yashtawhare/chatminds.git /opt/chatminds
cd /opt/chatminds

# Set up environment
cp .env.production .env
nano .env  # Edit with your values
```

### 4. Deploy

```bash
# Build and start containers
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

## 🌐 Application Structure

After deployment, your application will be accessible via:

- **Frontend (Main App)**: `http://your-domain/`
- **Backend API**: `http://your-domain/api/`
- **API Documentation**: `http://your-domain/api/docs`
- **Chatbot Widget**: `http://your-domain/widget/`

## 📊 Service Management

### Common Commands

```bash
# View status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update application
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Management

```bash
# Access SQLite database
docker-compose exec frontend sqlite3 askai.db

# Backup database
docker-compose exec frontend cp askai.db /app/data/backup-$(date +%Y%m%d).db

# View database tables
docker-compose exec frontend sqlite3 askai.db ".tables"
```

## 🔒 Security Considerations

### 1. Change Default Passwords
- Admin password: Login and change immediately
- Flask secret key: Use a strong, random key

### 2. Environment Variables
```env
# Use strong, unique values
FLASK_SECRET_KEY=your-very-long-random-secret-key
OPENAI_API_KEY=sk-your-real-openai-key
```

### 3. SSL/TLS Setup
- Use Let's Encrypt for free SSL certificates
- Uncomment the HTTPS server block in `nginx/default.conf`
- Update your domain name in the configuration

### 4. Firewall Configuration
```bash
# Check firewall status
sudo ufw status

# Allow specific IPs only (optional)
sudo ufw allow from YOUR_IP_ADDRESS to any port 22
```

## 🚨 Troubleshooting

### Common Issues

1. **Services won't start:**
   ```bash
   docker-compose logs
   # Check for missing environment variables or port conflicts
   ```

2. **Permission denied errors:**
   ```bash
   sudo chown -R $USER:$USER /opt/chatminds
   ```

3. **API connection issues:**
   - Check that backend service is running: `docker-compose ps`
   - Verify firewall rules: `sudo ufw status`
   - Check backend logs: `docker-compose logs backend`

4. **Database issues:**
   ```bash
   # Recreate database
   docker-compose exec frontend rm -f askai.db
   # Visit /create_tables and /seed endpoints
   ```

### Health Checks

```bash
# Check if services are responding
curl http://localhost/health
curl http://localhost/api/docs

# Check Docker containers
docker-compose ps
docker stats
```

## 📈 Scaling and Optimization

### Performance Tuning

1. **Increase resources:**
   - Upgrade droplet size for more CPU/RAM
   - Use DigitalOcean Spaces for file storage

2. **Database optimization:**
   - Consider PostgreSQL for production
   - Set up database backups

3. **Caching:**
   - Add Redis for session storage
   - Implement API response caching

### High Availability

1. **Load Balancer:**
   - Use DigitalOcean Load Balancer
   - Multiple droplet instances

2. **Database:**
   - Managed PostgreSQL database
   - Regular automated backups

## 💰 Cost Optimization

### Recommended Droplet Sizes

- **Development/Testing**: 2GB RAM ($12/month)
- **Small Production**: 4GB RAM ($24/month)
- **Medium Production**: 8GB RAM ($48/month)

### Additional Services

- **Load Balancer**: $12/month (if needed)
- **Managed Database**: Starting at $15/month
- **Spaces (Storage)**: $5/month for 250GB

## 📞 Support

### Logs and Monitoring

```bash
# Application logs
docker-compose logs -f

# System logs
sudo journalctl -u docker
sudo tail -f /var/log/nginx/error.log

# Resource monitoring
htop
df -h
```

### Backup Strategy

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec frontend cp askai.db /app/data/backup_$DATE.db
tar -czf /opt/backups/chatminds_$DATE.tar.gz /opt/chatminds/data
```

## 🔄 Updates and Maintenance

### Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update application
cd /opt/chatminds
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### SSL Certificate Renewal

```bash
# Let's Encrypt certificates auto-renew
# Test renewal
sudo certbot renew --dry-run
```

---

## 🎉 You're All Set!

Your ChatMinds application should now be running on DigitalOcean. Visit your domain or droplet IP to start using the application.

For additional support or questions, please check the repository issues or create a new one.