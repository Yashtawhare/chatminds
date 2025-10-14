# DigitalOcean Deployment - Quick Reference

## 🚀 One-Command Deployment

For the fastest deployment, run this on your DigitalOcean droplet:

```bash
curl -sSL https://raw.githubusercontent.com/Yashtawhare/chatminds/main/deploy/setup-server.sh | bash
```

Then:
```bash
cd /opt/chatminds
nano .env  # Add your OPENAI_API_KEY and other settings
newgrp docker && ./deploy/deploy.sh
```

## 🔑 Required Environment Variables

Before deployment, you MUST set these in your `.env` file:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
FLASK_SECRET_KEY=your-secure-random-string-here
DOMAIN_NAME=yourdomain.com
```

## 🌐 Access Points

After deployment:
- **Main App**: `http://your-domain/`
- **API Docs**: `http://your-domain/api/docs`
- **Chatbot Widget**: `http://your-domain/widget/`

## 🔧 First-Time Setup

1. Visit: `http://your-domain/create_tables`
2. Visit: `http://your-domain/seed`
3. Login with: `admin` / `admin`
4. **Change the admin password immediately!**

## 🆘 Quick Commands

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Update application
git pull && docker-compose down && docker-compose up -d --build
```

## 🔒 SSL Setup (Optional)

```bash
./deploy/setup-ssl.sh yourdomain.com
```

## 💡 Minimum Requirements

- **Droplet**: 2GB RAM Ubuntu 22.04
- **Domain**: Optional but recommended
- **OpenAI API Key**: Required for AI features

---

For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)