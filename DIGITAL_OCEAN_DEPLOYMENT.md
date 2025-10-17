# 🚀 ChatMinds Digital Ocean Deployment Guide

This comprehensive guide will walk you through deploying your ChatMinds application on Digital Ocean from start to finish.

## 📋 Prerequisites

### 1. Digital Ocean Account
- Create an account at [digitalocean.com](https://digitalocean.com)
- Add a payment method
- Generate an API token (optional, for automated deployments)

### 2. Domain Name (Recommended)
- Purchase a domain from any registrar (Namecheap, GoDaddy, etc.)
- You'll configure DNS after creating your droplet

### 3. OpenAI API Key
- Create account at [platform.openai.com](https://platform.openai.com)
- Generate an API key from [API Keys page](https://platform.openai.com/api-keys)
- Add billing information if required

## 🖥️ Step 1: Create Digital Ocean Droplet

### Option A: Using Digital Ocean Web Interface

1. **Login to Digital Ocean Dashboard**
   - Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
   
2. **Create New Droplet**
   - Click "Create" → "Droplets"
   
3. **Choose Configuration:**
   ```
   Image: Ubuntu 22.04 LTS
   Plan: 
     - Basic: $24/month (4GB RAM, 2 vCPUs, 80GB SSD) [Recommended]
     - Or Basic: $12/month (2GB RAM, 1 vCPU, 50GB SSD) [Minimum]
   
   Region: Choose closest to your users
   Authentication: SSH Key (recommended) or Password
   ```

4. **Configure Droplet:**
   - Add your SSH key (generate one if needed)
   - Choose a hostname (e.g., `chatminds-prod`)
   - Add tags: `chatminds`, `production`

5. **Create Droplet**
   - Click "Create Droplet"
   - Wait 2-3 minutes for provisioning
   - Note the IP address

### Option B: Using DigitalOcean CLI (doctl)

```bash
# Install doctl
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz | tar -xzv
sudo mv doctl /usr/local/bin

# Authenticate
doctl auth init

# Create droplet
doctl compute droplet create chatminds-prod \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc1 \
  --ssh-keys your-ssh-key-id \
  --tag-names chatminds,production
```

## 🌐 Step 2: Configure Domain (Optional but Recommended)

### A. Point Domain to Droplet
1. Get your droplet's IP address from Digital Ocean dashboard
2. Go to your domain registrar's DNS settings
3. Create/update these DNS records:
   ```
   Type: A Record
   Name: @ (or blank)
   Value: your-droplet-ip
   TTL: 300 (5 minutes)
   
   Type: A Record  
   Name: www
   Value: your-droplet-ip
   TTL: 300
   ```

### B. Using Digital Ocean Domains (Optional)
```bash
# Add domain to Digital Ocean
doctl compute domain create yourdomain.com --ip-address your-droplet-ip

# Create www subdomain
doctl compute domain records create yourdomain.com \
  --record-type A \
  --record-name www \
  --record-data your-droplet-ip
```

## 🔐 Step 3: Connect to Your Droplet

### Using SSH Key (Recommended)
```bash
ssh root@your-droplet-ip
```

### Using Password
```bash
ssh root@your-droplet-ip
# Enter password when prompted
```

### First Time Setup
```bash
# Update system
apt update && apt upgrade -y

# Create non-root user (optional but recommended)
adduser chatminds
usermod -aG sudo chatminds
```

## 🚀 Step 4: Deploy ChatMinds (Automated)

### Quick Deployment (Recommended)
```bash
# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/yourusername/chatminds/main/deploy.sh -o deploy.sh
chmod +x deploy.sh

# Run with your configuration
./deploy.sh --domain yourdomain.com --openai-key sk-your-api-key
```

### Manual Configuration
```bash
# If you want to configure manually
./deploy.sh
# Then edit .env file when prompted
nano /opt/chatminds/.env
```

## 🔧 Step 5: Manual Deployment (Alternative)

If you prefer manual control:

### A. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git and other tools
sudo apt install -y git curl wget nano htop ufw
```

### B. Clone and Configure
```bash
# Clone your repository
git clone https://github.com/yourusername/chatminds.git /opt/chatminds
cd /opt/chatminds

# Create environment file
cp .env.example .env
nano .env  # Edit with your values
```

### C. Update Configuration
```bash
# Update nginx configuration
nano nginx/nginx.conf
# Replace 'your-domain.com' with your actual domain

# Make scripts executable
chmod +x deploy.sh health_check.sh validate_env.sh
```

### D. Build and Start
```bash
# Build and start services
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

## 🔒 Step 6: SSL/HTTPS Setup

### Option A: Let's Encrypt (Free SSL)
```bash
# Install Certbot
sudo snap install --classic certbot

# Stop nginx temporarily
cd /opt/chatminds
docker-compose stop nginx

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/ssl/certificate.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./nginx/ssl/private.key
sudo chown $USER:$USER ./nginx/ssl/*

# Update nginx config to enable SSL
sed -i 's/# ssl_certificate/ssl_certificate/g' nginx/nginx.conf
sed -i 's/# ssl_certificate_key/ssl_certificate_key/g' nginx/nginx.conf
sed -i 's/# ssl_protocols/ssl_protocols/g' nginx/nginx.conf
sed -i 's/# ssl_ciphers/ssl_ciphers/g' nginx/nginx.conf

# Restart services
docker-compose up -d
```

### Option B: Cloudflare SSL (Alternative)
1. Add your domain to Cloudflare
2. Update nameservers to Cloudflare's
3. Enable "Flexible SSL" in Cloudflare dashboard
4. No certificate installation needed on server

## 🔥 Step 7: Configure Firewall

```bash
# Reset firewall
sudo ufw --force reset

# Set defaults
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow necessary ports
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status verbose
```

## ✅ Step 8: Verify Deployment

### Health Checks
```bash
cd /opt/chatminds

# Check service status
docker-compose ps

# Check health endpoints
curl -I http://localhost/health
curl -I http://localhost:8000/health

# View logs
docker-compose logs -f chatminds-web
docker-compose logs -f chatminds-llm
docker-compose logs -f nginx
```

### Test Application
1. **Visit your website:**
   - `http://yourdomain.com` or `http://your-droplet-ip`
   - Should redirect to HTTPS if SSL is configured

2. **Create first admin account:**
   - Visit `/register` to create admin account
   - Or use the seeding endpoint if available

3. **Test functionality:**
   - Upload a document
   - Start a chat
   - Test AI responses

## 📊 Step 9: Monitoring and Maintenance

### Set Up Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Set up log rotation
sudo nano /etc/logrotate.d/chatminds
```

### Backup Setup
```bash
# Create backup script
cd /opt/chatminds
chmod +x backup_chatminds.sh

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /opt/chatminds/backup_chatminds.sh
```

### Update Process
```bash
# Regular updates
cd /opt/chatminds
git pull origin main
docker-compose build --no-cache
docker-compose up -d

# System updates
sudo apt update && sudo apt upgrade -y
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

#### 2. SSL Certificate Issues
```bash
# Renew certificates
sudo certbot renew --dry-run

# Check certificate expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

#### 3. Out of Memory
```bash
# Check memory usage
free -h
docker stats

# Add swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### 4. High CPU Usage
```bash
# Check processes
htop
docker stats

# Optimize worker count
nano .env
# Adjust GUNICORN_WORKERS
docker-compose restart chatminds-web
```

#### 5. Database Issues
```bash
# Backup database
docker-compose exec chatminds-web cp /app/askai.db /app/data/backup.db

# Reset database
docker-compose exec chatminds-web python -c "from app import create_tables; create_tables()"
```

### Performance Optimization

#### 1. Upgrade Droplet
```bash
# Via DigitalOcean dashboard or CLI
doctl compute droplet-action resize droplet-id --size s-4vcpu-8gb --disk
```

#### 2. Add CDN
- Use Cloudflare for free CDN
- Configure caching rules
- Enable image optimization

#### 3. Database Optimization
- Consider PostgreSQL for high traffic
- Add database indexes
- Implement connection pooling

## 🎯 Production Checklist

- [ ] ✅ Droplet created with sufficient resources
- [ ] ✅ Domain configured and DNS propagated
- [ ] ✅ SSH access working
- [ ] ✅ Application deployed successfully
- [ ] ✅ SSL certificate installed and working
- [ ] ✅ Firewall configured properly
- [ ] ✅ Health checks passing
- [ ] ✅ Backup system in place
- [ ] ✅ Monitoring set up
- [ ] ✅ Admin account created
- [ ] ✅ Test uploads and chat working
- [ ] ✅ Email notifications configured (if needed)
- [ ] ✅ Rate limiting enabled
- [ ] ✅ Log rotation configured
- [ ] ✅ Update process documented

## 🆘 Support and Next Steps

### Getting Help
- Check logs: `docker-compose logs -f`
- Review configuration files
- Test individual services
- Check Digital Ocean status page
- Contact support if needed

### Scaling Considerations
- **Traffic Growth**: Upgrade droplet size
- **Multiple Regions**: Deploy in multiple regions
- **Load Balancing**: Use Digital Ocean Load Balancer
- **Database**: Migrate to managed PostgreSQL
- **File Storage**: Use Digital Ocean Spaces
- **CDN**: Implement proper CDN solution

### Security Hardening
- Regular security updates
- Implement fail2ban
- Set up monitoring alerts
- Regular backup testing
- Access log monitoring
- Rate limiting tuning

---

**🎉 Congratulations!** Your ChatMinds application should now be running smoothly on Digital Ocean.

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Verify configuration files
4. Test network connectivity
5. Check Digital Ocean dashboard for any alerts

Remember to:
- Keep your system updated
- Monitor resource usage
- Regularly backup your data
- Renew SSL certificates
- Update your application code

Your application should be accessible at:
- **Production URL**: `https://yourdomain.com`
- **Admin Panel**: `https://yourdomain.com/admin` (if implemented)
- **Health Check**: `https://yourdomain.com/health`