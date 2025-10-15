# SSL Certificate Setup for ChatMinds

## Option 1: Let's Encrypt (Free SSL - Recommended)

### Prerequisites
- Domain name pointing to your Digital Ocean droplet
- Ports 80 and 443 open

### Installation Steps

1. **Install Certbot:**
```bash
sudo apt update
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

2. **Stop Nginx temporarily:**
```bash
docker-compose stop nginx
```

3. **Generate SSL certificates:**
```bash
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

4. **Copy certificates to nginx directory:**
```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/certificate.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/private.key
sudo chown $USER:$USER ./nginx/ssl/*
```

5. **Update nginx configuration:**
Edit `nginx/nginx.conf` and uncomment the SSL lines:
```nginx
ssl_certificate /etc/nginx/ssl/certificate.crt;
ssl_certificate_key /etc/nginx/ssl/private.key;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
```

Also comment out the development line:
```nginx
# listen 80;  # Comment this line
```

6. **Restart services:**
```bash
docker-compose up -d
```

7. **Set up auto-renewal:**
```bash
sudo crontab -e
```
Add this line:
```
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx
```

## Option 2: Self-Signed Certificate (Development/Testing)

1. **Generate self-signed certificate:**
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./nginx/ssl/private.key \
    -out ./nginx/ssl/certificate.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

2. **Follow steps 5-6 from Option 1**

## Option 3: Upload Your Own Certificate

1. **Copy your certificate files:**
```bash
cp your-certificate.crt ./nginx/ssl/certificate.crt
cp your-private-key.key ./nginx/ssl/private.key
```

2. **Follow steps 5-6 from Option 1**

## Troubleshooting

### Check SSL certificate:
```bash
openssl x509 -in ./nginx/ssl/certificate.crt -text -noout
```

### Test SSL configuration:
```bash
curl -I https://your-domain.com
```

### View nginx logs:
```bash
docker-compose logs nginx
```

### Verify certificate renewal:
```bash
sudo certbot renew --dry-run
```