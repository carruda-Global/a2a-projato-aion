#!/bin/bash
# AION SallesJam — Hetzner Cloud Setup
# Run as root on a fresh Ubuntu 22.04 CX31 (8 vCPU, 16GB RAM, €12/mês)
# Usage: curl -sSL https://raw.githubusercontent.com/carruda-Global/engenheiro-producao-ai/main/deploy/hetzner-setup.sh | bash

set -e

echo "=== AION SallesJam — Hetzner Deploy ==="

# 1. System update
apt-get update -qq && apt-get upgrade -y -qq

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# 3. Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 4. Install Nginx + Certbot
apt-get install -y -qq nginx certbot python3-certbot-nginx

# 5. Clone repo
git clone https://github.com/carruda-Global/engenheiro-producao-ai.git /opt/aion
cd /opt/aion

# 6. Create production .env from Render env vars
cat > /opt/aion/.env.production << 'ENVEOF'
APP_ENV=production
BASE_URL=https://api.global-engenharia.com
A2A_ENABLED=true
A2A_BASE_URL=https://api.global-engenharia.com
# Fill these from Render dashboard:
DEEPSEEK_API_KEY=
SUPABASE_URL=
SUPABASE_API_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
RESEND_API_KEY=
DEVTO_API_KEY=
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
ENVEOF

echo ">>> Edit /opt/aion/.env.production with your keys before starting"

# 7. Create docker-compose.production.yml
cat > /opt/aion/docker-compose.production.yml << 'DCEOF'
version: "3.9"
services:
  aion-api:
    build: .
    restart: always
    ports:
      - "8000:8000"
    env_file: .env.production
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  aion-mcp-regulatory:
    build: .
    restart: always
    ports:
      - "8010:8010"
    env_file: .env.production
    command: uvicorn src.mcp.regulatory_server:regulatory_app --host 0.0.0.0 --port 8010 --workers 2

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - aion-api
DCEOF

# 8. Nginx config
mkdir -p /opt/aion/deploy
cat > /opt/aion/deploy/nginx.conf << 'NGEOF'
server {
    listen 80;
    server_name api.global-engenharia.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.global-engenharia.com;

    ssl_certificate /etc/letsencrypt/live/api.global-engenharia.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.global-engenharia.com/privkey.pem;

    location / {
        proxy_pass http://aion-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }
}
NGEOF

# 9. Auto-deploy script (runs on git push via webhook or cron)
cat > /opt/aion/deploy/auto-update.sh << 'AUEOF'
#!/bin/bash
cd /opt/aion
git pull origin main
docker-compose -f docker-compose.production.yml build --no-cache aion-api
docker-compose -f docker-compose.production.yml up -d --no-deps aion-api
echo "Deploy completed: $(date)"
AUEOF
chmod +x /opt/aion/deploy/auto-update.sh

# 10. Cron for auto-deploy every 5 min (polls git)
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/aion/deploy/auto-update.sh >> /var/log/aion-deploy.log 2>&1") | crontab -

echo ""
echo "=== Setup completo ==="
echo "1. Edite /opt/aion/.env.production com suas chaves"
echo "2. Configure DNS: api.global-engenharia.com -> $(curl -s ifconfig.me)"
echo "3. Rode: certbot --nginx -d api.global-engenharia.com"
echo "4. Rode: docker-compose -f /opt/aion/docker-compose.production.yml up -d"
echo ""
echo "Servidor IP: $(curl -s ifconfig.me)"
