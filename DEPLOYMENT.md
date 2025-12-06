# Deployment Guide - Miss France Prediction App

## Prerequisites

- Ubuntu Server (20.04 or later)
- Python 3.8+
- PostgreSQL
- Nginx (for reverse proxy)
- Git

## Step 1: Server Setup

### Install Required Packages

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git
```

### Create PostgreSQL Database

```bash
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE miss;
CREATE USER missuser WITH PASSWORD 'your_secure_password_here';
ALTER ROLE missuser SET client_encoding TO 'utf8';
ALTER ROLE missuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE missuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE miss TO missuser;
\q
```

## Step 2: Clone Repository

```bash
cd /opt
sudo git clone https://github.com/y4nnr/miss.git
sudo chown -R $USER:$USER /opt/miss
cd /opt/miss
```

## Step 3: Python Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Environment Configuration

```bash
cp .env.example .env
nano .env
```

Update the `.env` file with:
```
SECRET_KEY=generate-a-strong-random-secret-key-here
DATABASE_URL=postgresql://missuser:your_secure_password_here@localhost/miss
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5002
```

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 5: Initialize Database

```bash
source venv/bin/activate
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Step 6: Create Systemd Service

Create `/etc/systemd/system/miss.service`:

```bash
sudo nano /etc/systemd/system/miss.service
```

Add:
```ini
[Unit]
Description=Miss France Prediction App
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/miss
Environment="PATH=/opt/miss/venv/bin"
EnvironmentFile=/opt/miss/.env
ExecStart=/opt/miss/venv/bin/python /opt/miss/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable miss
sudo systemctl start miss
sudo systemctl status miss
```

## Step 7: Configure Nginx

Create `/etc/nginx/sites-available/miss`:

```bash
sudo nano /etc/nginx/sites-available/miss
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Change to your domain or IP

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/miss/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/miss /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 8: Firewall Configuration

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 9: SSL Certificate (Optional but Recommended)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Maintenance Commands

### View logs
```bash
sudo journalctl -u miss -f
```

### Restart app
```bash
sudo systemctl restart miss
```

### Update from GitHub
```bash
cd /opt/miss
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart miss
```

## Security Notes

1. Change the default PostgreSQL password
2. Use a strong SECRET_KEY
3. Keep the `.env` file secure (not in git)
4. Regularly update dependencies
5. Use SSL/HTTPS in production

