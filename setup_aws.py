import os

files = {
    ".github/workflows/deploy.yml": """name: Deploy SmartLLM to AWS EC2

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ secrets.EC2_SSH_KEY }}

      - name: Deploy to EC2
        run: |
          ssh -o StrictHostKeyChecking=no ubuntu@${{ secrets.EC2_HOST }} << 'EOF'
            cd /home/ubuntu/smartllm
            git pull origin main
            
            # Fetch secrets dynamically from AWS Secrets Manager
            aws secretsmanager get-secret-value --region us-east-1 --secret-id smartllm/prod/.env --query SecretString --output text > .env
            
            # Rebuild and restart containers via production compose file
            docker-compose -f docker-compose.prod.yml up -d --build
          EOF
""",
    "docker-compose.prod.yml": """version: '3.8'

# Production Compose File
# Excludes Postgres and Redis, assuming AWS RDS and ElastiCache are used.

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: smartllm-api-prod
    restart: always
    env_file:
      - .env
    ports:
      - "8000:8000"
    networks:
      - smartllm_prod_network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: smartllm-web-prod
    restart: always
    env_file:
      - .env
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_started
    networks:
      - smartllm_prod_network

networks:
  smartllm_prod_network:
    driver: bridge
""",
    "nginx/smartllm.conf": """server {
    listen 80;
    server_name smartllm.com www.smartllm.com api.smartllm.com;
    
    # Enforce HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# Frontend Route
server {
    listen 443 ssl http2;
    server_name smartllm.com www.smartllm.com;

    ssl_certificate /etc/letsencrypt/live/smartllm.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/smartllm.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API Route
server {
    listen 443 ssl http2;
    server_name api.smartllm.com;

    ssl_certificate /etc/letsencrypt/live/api.smartllm.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.smartllm.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
""",
    "deploy.sh": """#!/bin/bash
set -e

echo "Starting SmartLLM Deployment..."

sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose nginx certbot python3-certbot-nginx awscli

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu || true

echo "Fetching production secrets..."
aws secretsmanager get-secret-value --region us-east-1 --secret-id smartllm/prod/.env --query SecretString --output text > .env

echo "Building Docker containers..."
sudo docker-compose -f docker-compose.prod.yml up -d --build

echo "Configuring NGINX..."
sudo cp nginx/smartllm.conf /etc/nginx/sites-available/smartllm
sudo ln -sf /etc/nginx/sites-available/smartllm /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# sudo certbot --nginx -d smartllm.com -d www.smartllm.com -d api.smartllm.com --non-interactive --agree-tos -m admin@smartllm.com
sudo systemctl restart nginx
echo "Deployment Complete!"
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("AWS deployment scripts created.")
