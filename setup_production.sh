#!/bin/bash
# Production setup script for Ubuntu Server

set -e

echo "🚀 Setting up Miss France Prediction App on Ubuntu Server"
echo "=========================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/miss
sudo chown $USER:$USER /opt/miss

# Clone repository
echo "📥 Cloning repository..."
cd /opt
if [ -d "miss" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd miss
    git pull
else
    git clone https://github.com/y4nnr/miss.git
    cd miss
fi

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit /opt/miss/.env with your configuration:"
    echo "   - SECRET_KEY: Generate with: python3 -c \"import secrets; print(secrets.token_hex(32))\""
    echo "   - DATABASE_URL: Update with your PostgreSQL credentials"
    echo ""
    read -p "Press Enter after you've configured .env file..."
fi

# Initialize database
echo "🗄️  Initializing database..."
source venv/bin/activate
python3 -c "from app import app, db; app.app_context().push(); db.create_all()" || echo "Database might already exist"

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/miss.service > /dev/null <<EOF
[Unit]
Description=Miss France Prediction App
After=network.target postgresql.service

[Service]
User=$USER
Group=$USER
WorkingDirectory=/opt/miss
Environment="PATH=/opt/miss/venv/bin"
EnvironmentFile=/opt/miss/.env
ExecStart=/opt/miss/venv/bin/python /opt/miss/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "▶️  Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable miss
sudo systemctl start miss

# Configure Nginx
echo "🌐 Configuring Nginx..."
read -p "Enter your domain name or IP address: " DOMAIN

sudo tee /etc/nginx/sites-available/miss > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /opt/miss/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/miss /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit /opt/miss/.env with your configuration"
echo "   2. Restart the service: sudo systemctl restart miss"
echo "   3. Check status: sudo systemctl status miss"
echo "   4. View logs: sudo journalctl -u miss -f"
echo ""
echo "🌐 Your app should be available at: http://$DOMAIN"

