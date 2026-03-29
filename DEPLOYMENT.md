# Infrastructure Fatigue Monitoring - Deployment Guide

**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: March 30, 2026

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start (Development)](#quick-start-development)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Nginx Configuration](#nginx-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Checklist](#security-checklist)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- Python 3.11+
- 2GB RAM minimum
- 100MB disk space
- Linux/Unix (Ubuntu 20.04+ recommended) or macOS

### Required Software
- Git
- Python pip/venv
- Gunicorn (production)
- Nginx (optional, recommended for production)
- Supervisor or systemd (for process management)

### Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip nginx supervisor git

# macOS
brew install python@3.11 nginx supervisor
```

---

## Quick Start (Development)

### 1. Clone/Setup Project
```bash
cd c:\Users\sudha\Infrastructure_Fatigue_Monitoring
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Development Server
```bash
python app.py
```
Access at: `http://localhost:5000`

### 3. Environment Setup
```bash
cp .env.example .env
# Edit .env with your settings
```

---

## Production Deployment

### Step 1: System Setup
```bash
# Create application user (non-root)
sudo useradd -m -s /bin/bash inframonitor

# Navigate to project directory
cd /opt/infrastructure-fatigue-monitoring

# Setup Python virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools
pip install -r requirements-prod.txt
```

### Step 2: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with production values
sudo nano .env
```

**Required Environment Variables**:
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate-random-key>
HOST=0.0.0.0
PORT=5000
WORKERS=4
DATA_PATH=/opt/data/vibration_data.csv
LOG_LEVEL=INFO
LOG_FILE=/var/log/inframonitor/app.log
```

**Generate Secret Key**:
```python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Create Systemd Service
Create `/etc/systemd/system/inframonitor.service`:

```ini
[Unit]
Description=Infrastructure Fatigue Monitoring Dashboard
After=network.target

[Service]
Type=notify
User=inframonitor
WorkingDirectory=/opt/infrastructure-fatigue-monitoring
Environment="PATH=/opt/infrastructure-fatigue-monitoring/venv/bin"
EnvironmentFile=/opt/infrastructure-fatigue-monitoring/.env
ExecStart=/opt/infrastructure-fatigue-monitoring/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 0.0.0.0:5000 \
    --timeout 30 \
    --access-logfile /var/log/inframonitor/access.log \
    --error-logfile /var/log/inframonitor/error.log \
    wsgi:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 4: Enable & Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable inframonitor
sudo systemctl start inframonitor
sudo systemctl status inframonitor
```

### Step 5: Gunicorn Manual Start (Alternative)
```bash
cd /opt/infrastructure-fatigue-monitoring
source venv/bin/activate
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
```

---

## Docker Deployment

### Step 1: Create Dockerfile
Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000')" || exit 1

# Run Gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
```

### Step 2: Create Docker Compose
Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  inframonitor:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - WORKERS=4
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Step 3: Deploy with Docker
```bash
# Build image
docker build -t inframonitor:latest .

# Run container
docker run -d -p 5000:5000 --name inframonitor inframonitor:latest

# Or use Docker Compose
docker-compose up -d
```

---

## Nginx Configuration

Create `/etc/nginx/sites-available/inframonitor`:

```nginx
upstream inframonitor {
    server localhost:5000;
}

server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 10M;

    location / {
        proxy_pass http://inframonitor;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /opt/infrastructure-fatigue-monitoring/static/;
        expires 30d;
    }
}
```

Enable Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/inframonitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Monitoring & Logging

### Log Files
- **Application Log**: `/var/log/inframonitor/app.log`
- **Access Log**: `/var/log/inframonitor/access.log`
- **Error Log**: `/var/log/inframonitor/error.log`

### View Logs
```bash
# Systemd logs
sudo journalctl -u inframonitor -f

# Application logs
tail -f /var/log/inframonitor/app.log

# Nginx logs
tail -f /var/log/nginx/access.log
```

### Monitor Service Health
```bash
# Check service status
sudo systemctl status inframonitor

# Restart service
sudo systemctl restart inframonitor

# Stop service
sudo systemctl stop inframonitor
```

### Performance Monitoring
```bash
# Check memory/CPU
ps aux | grep gunicorn

# Check port
sudo netstat -tlnp | grep 5000

# Check connectivity
curl -I http://localhost:5000
```

---

## Security Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Configure firewall rules
- [ ] Limit file permissions: `chmod 600 .env`
- [ ] Run application as non-root user
- [ ] Keep dependencies updated: `pip install --upgrade -r requirements-prod.txt`
- [ ] Enable Nginx security headers
- [ ] Disable directory listing
- [ ] Configure backup strategy for CSV data
- [ ] Monitor logs for suspicious activity
- [ ] Set up rate limiting on Nginx
- [ ] Use strong passwords for any authentication
- [ ] Enable SELinux/AppArmor if available

---

## SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renew (systemd timer)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Troubleshooting

### Service Won't Start
```bash
# Check errors
sudo systemctl status inframonitor
sudo journalctl -u inframonitor -n 50

# Check port conflicts
sudo lsof -i :5000

# Verify environment variables
sudo systemctl cat inframonitor
```

### High Memory Usage
- Reduce worker count in Gunicorn: `--workers 2`
- Check data file size
- Limit chart data lookback in app.py

### Database/CSV Issues
```bash
# Verify CSV format
head -5 data/vibration_data.csv

# Check file permissions
ls -la data/vibration_data.csv

# Repair CSV if corrupted
python3 scripts/repair_csv.py
```

### Nginx 502 Bad Gateway
- Check if Gunicorn is running: `sudo systemctl status inframonitor`
- Check upstream server: `sudo netstat -tlnp | grep 5000`
- Check Nginx error logs: `tail -f /var/log/nginx/error.log`

### Performance Issues
```bash
# Check system resources
free -h
top

# Increase Gunicorn workers
# Edit /etc/systemd/system/inframonitor.service
# Change: --workers 8

# Reload systemd and restart
sudo systemctl daemon-reload
sudo systemctl restart inframonitor
```

---

## Scaling for Production

### Load Balancing
Use Nginx to distribute requests across multiple Gunicorn instances:
```nginx
upstream inframonitor_workers {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}
```

### Database Migration
For larger deployments, consider:
- PostgreSQL instead of CSV
- Redis for caching
- Elasticsearch for advanced analytics

### Monitoring Stack
Recommended additions:
- Prometheus for metrics
- Grafana for dashboards
- ELK Stack for centralized logging
- Sentry for error tracking

---

## Backup & Recovery

### Backup Strategy
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/inframonitor"
DATE=$(date +%Y%m%d_%H%M%S)
cp -r /opt/infrastructure-fatigue-monitoring/data $BACKUP_DIR/data_$DATE
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /opt/infrastructure-fatigue-monitoring
```

### Recovery
```bash
# Restore from backup
tar -xzf /backups/inframonitor/app_20260330.tar.gz -C /opt/
systemctl restart inframonitor
```

---

## Support & Documentation

- **Project Repo**: [GitHub Repository]
- **Documentation**: [Project Wiki]
- **Issues**: [GitHub Issues]
- **Contact**: infrastructure-monitoring@yourdomain.com

---

## Changelog

### v1.0 (2026-03-30)
- Initial production deployment guide
- 1000 record dataset support
- Gunicorn + Nginx setup
- Docker deployment option
- SSL/TLS configuration
