#!/bin/bash
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
