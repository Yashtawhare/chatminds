# 🚀 ChatMinds Digital Ocean Deployment - Complete Setup

## 📂 What's Been Created

I've set up a complete Docker-based deployment system for your ChatMinds application with the following files:

### Core Deployment Files
- **`docker-compose.yml`** - Multi-container orchestration
- **`chatminds/Dockerfile`** - Flask web app container
- **`chatminds-llm/Dockerfile`** - FastAPI LLM service container
- **`nginx/nginx.conf`** - Reverse proxy configuration

### Deployment Scripts
- **`deploy.sh`** - Automated deployment script ⭐
- **`health_check.sh`** - Service health monitoring
- **`backup.sh`** - Database and data backup utility

### Configuration
- **`.env.example`** - Environment variables template
- **`.gitignore`** - Git ignore rules for sensitive files
- **`DEPLOYMENT.md`** - Comprehensive deployment guide
- **`SSL_SETUP.md`** - SSL certificate setup instructions

## 🎯 Quick Start (Recommended)

### 1. Push to GitHub
```bash
cd "d:\GITHUB-REPOS\chatminds"
git add .
git commit -m "Add Digital Ocean deployment configuration"
git push origin main
```

### 2. On Your Digital Ocean Droplet
```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Run the automated deployment
curl -fsSL https://raw.githubusercontent.com/Yashtawhare/chatminds/main/deploy.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
```

The script will handle everything automatically!

## 🔧 Manual Setup Process

If you prefer manual control:

### Step 1: Server Setup
```bash
# Create droplet with Ubuntu 22.04
# Minimum: 2GB RAM, 1 CPU, 25GB disk
# Recommended: 4GB RAM, 2 CPU, 50GB disk
```

### Step 2: Install Dependencies
```bash
ssh root@your-droplet-ip

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 3: Deploy Application
```bash
# Clone repository
git clone https://github.com/Yashtawhare/chatminds.git /opt/chatminds
cd /opt/chatminds

# Configure environment
cp .env.example .env
nano .env  # Add your OpenAI API key

# Update domain in nginx config
nano nginx/nginx.conf  # Replace 'your-domain.com'

# Build and start services
docker-compose build
docker-compose up -d
```

## 🌐 Access Your Application

- **Web Interface**: `http://your-domain.com` or `http://your-droplet-ip`
- **Admin Setup**: Visit `/seed` to create admin account
- **Default Login**: admin/admin (change immediately!)

## 🔒 SSL Setup (Production)

For HTTPS in production:

```bash
# Install Certbot
sudo snap install --classic certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/certificate.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/private.key

# Update nginx config (uncomment SSL lines)
# Restart services
docker-compose restart nginx
```

## 📊 Management Commands

### Check Status
```bash
./health_check.sh your-domain.com
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs chatminds-web
docker-compose logs chatminds-llm
```

### Update Application
```bash
git pull origin main
docker-compose build
docker-compose up -d
```

### Backup Data
```bash
./backup.sh
```

### Restart Services
```bash
docker-compose restart
```

## 🔥 Firewall & Security

The deployment automatically configures:
- UFW firewall (ports 22, 80, 443)
- Nginx reverse proxy
- Container isolation
- Environment variable security

## 💡 Key Features

### Architecture Benefits
- **Scalable**: Easy to add more workers
- **Secure**: Containerized services
- **Maintainable**: Docker orchestration
- **Monitored**: Health checks and logging
- **Reliable**: Auto-restart on failure

### Services Structure
```
Internet → Nginx (80/443) → Flask App (5000) ← SQLite DB
                        └─→ FastAPI LLM (8000) ← OpenAI API
```

## 🔧 Customization

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your_key_here
FLASK_ENV=production
FLASK_DEBUG=false
```

### Scaling Options
- **Vertical**: Upgrade droplet size
- **Horizontal**: Add more app containers
- **Database**: Switch to PostgreSQL
- **Storage**: Use DigitalOcean Spaces

## 🐛 Troubleshooting

### Common Issues
1. **Services won't start**: Check logs with `docker-compose logs`
2. **Permission errors**: Run `sudo chown -R $USER:$USER /opt/chatminds`
3. **OpenAI API errors**: Verify API key in `.env`
4. **Database issues**: Run `docker-compose exec chatminds-web python -c "from app import create_tables; create_tables()"`

### Health Monitoring
```bash
# Quick health check
./health_check.sh

# Detailed service status
docker-compose ps
docker stats

# System resources
htop
df -h
```

## 📈 Production Recommendations

### Security
- [ ] Change default admin password
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Enable fail2ban
- [ ] Set up monitoring

### Performance
- [ ] Configure log rotation
- [ ] Set up database backups
- [ ] Monitor resource usage
- [ ] Configure CDN (optional)

### Maintenance
- [ ] Schedule automatic backups
- [ ] Set up update notifications
- [ ] Monitor SSL certificate expiry
- [ ] Regular security updates

## 🆘 Support & Next Steps

Your ChatMinds application is now ready for Digital Ocean deployment! 

**Immediate Actions:**
1. ✅ Commit and push changes to GitHub
2. ✅ Create Digital Ocean droplet
3. ✅ Run deployment script
4. ✅ Configure your domain
5. ✅ Set up SSL certificate
6. ✅ Create admin account

**Questions?** Check the logs, run health checks, and refer to the detailed guides in `DEPLOYMENT.md` and `SSL_SETUP.md`.

---
*Generated for ChatMinds deployment on Digital Ocean* 🚀