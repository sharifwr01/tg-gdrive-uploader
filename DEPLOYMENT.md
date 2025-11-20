# 🚀 Production Deployment Guide

এই গাইড Linux VPS/Cloud Server এ bot deploy করার জন্য।

## 📋 Prerequisites

- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Root বা sudo access
- Public IP বা Domain (webhook এর জন্য optional)

## 🔧 Server Setup

### Step 1: Server Update করুন

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Python 3.8+ Install করুন

```bash
sudo apt install python3 python3-pip python3-venv -y
```

### Step 3: Git Install করুন

```bash
sudo apt install git -y
```

## 📦 Bot Installation

### Step 1: Bot Clone করুন

```bash
cd /opt
sudo git clone https://github.com/sharifwr01/tg-gdrive-uploader telegram-bot
cd telegram-bot
```

### Step 2: Ownership পরিবর্তন করুন

```bash
sudo chown -R $USER:$USER /opt/telegram-bot
```

### Step 3: Virtual Environment তৈরি করুন

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Dependencies Install করুন

```bash
pip install -r requirements.txt
```

### Step 5: Configuration করুন

```bash
cp .env.example .env
nano .env
```

`.env` ফাইলে আপনার credentials fill করুন।

`credentials.json` ফাইল upload করুন:

```bash
# Local machine থেকে server এ copy করুন:
scp credentials.json user@server:/opt/telegram-bot/
```

## 🔄 Systemd Service Setup

### Step 1: Log Directory তৈরি করুন

```bash
sudo mkdir -p /var/log/telegram-bot
sudo chown $USER:$USER /var/log/telegram-bot
```

### Step 2: Service File তৈরি করুন

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

এই content paste করুন:

```ini
[Unit]
Description=Telegram File Upload Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/opt/telegram-bot
ExecStart=/opt/telegram-bot/venv/bin/python bot.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

StandardOutput=append:/var/log/telegram-bot/output.log
StandardError=append:/var/log/telegram-bot/error.log

[Install]
WantedBy=multi-user.target
```

**Important:** `YOUR_USERNAME` replace করুন আপনার actual username দিয়ে।

### Step 3: Service Enable ও Start করুন

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### Step 4: Status Check করুন

```bash
sudo systemctl status telegram-bot
```

## 📊 Monitoring

### Service Status দেখুন

```bash
sudo systemctl status telegram-bot
```

### Live Logs দেখুন

```bash
# Output logs
tail -f /var/log/telegram-bot/output.log

# Error logs
tail -f /var/log/telegram-bot/error.log

# Both together
tail -f /var/log/telegram-bot/*.log
```

### Service Restart করুন

```bash
sudo systemctl restart telegram-bot
```

### Service Stop করুন

```bash
sudo systemctl stop telegram-bot
```

## 🌐 Webhook Setup (Optional)

Polling এর পরিবর্তে webhook use করতে চাইলে:

### Requirements:
- Public domain বা IP
- SSL certificate (Let's Encrypt recommended)
- Port 8443 বা 443 open

### Step 1: SSL Certificate Setup করুন

```bash
sudo apt install certbot -y
sudo certbot certonly --standalone -d yourdomain.com
```

### Step 2: .env ফাইল Update করুন

```env
USE_WEBHOOK=True
WEBHOOK_URL=https://yourdomain.com:8443
PORT=8443
```

### Step 3: Firewall Configure করুন

```bash
sudo ufw allow 8443/tcp
sudo ufw reload
```

### Step 4: Bot Restart করুন

```bash
sudo systemctl restart telegram-bot
```

## 🔒 Security Best Practices

### 1. Firewall Setup করুন

```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8443/tcp  # Webhook port
sudo ufw reload
```

### 2. File Permissions Secure করুন

```bash
chmod 600 /opt/telegram-bot/.env
chmod 600 /opt/telegram-bot/credentials.json
```

### 3. Regular Updates করুন

```bash
cd /opt/telegram-bot
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart telegram-bot
```

### 4. Backup Strategy

Database backup script তৈরি করুন:

```bash
nano /opt/telegram-bot/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/telegram-bot-backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp /opt/telegram-bot/bot_database.db $BACKUP_DIR/bot_database_$DATE.db

# Keep only last 7 days backups
find $BACKUP_DIR -name "bot_database_*.db" -mtime +7 -delete
```

```bash
chmod +x /opt/telegram-bot/backup.sh
```

Cron job setup করুন:

```bash
crontab -e
```

```
# Daily backup at 2 AM
0 2 * * * /opt/telegram-bot/backup.sh
```

## 📈 Performance Optimization

### 1. Process Manager (PM2 Alternative)

Systemd ছাড়াও Supervisor use করতে পারেন:

```bash
sudo apt install supervisor -y
```

```bash
sudo nano /etc/supervisor/conf.d/telegram-bot.conf
```

```ini
[program:telegram-bot]
directory=/opt/telegram-bot
command=/opt/telegram-bot/venv/bin/python bot.py
user=YOUR_USERNAME
autostart=true
autorestart=true
stderr_logfile=/var/log/telegram-bot/error.log
stdout_logfile=/var/log/telegram-bot/output.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start telegram-bot
```

### 2. Log Rotation Setup

```bash
sudo nano /etc/logrotate.d/telegram-bot
```

```
/var/log/telegram-bot/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 YOUR_USERNAME YOUR_USERNAME
    sharedscripts
    postrotate
        systemctl reload telegram-bot > /dev/null 2>&1 || true
    endscript
}
```

### 3. Resource Monitoring

Install monitoring tools:

```bash
sudo apt install htop iotop -y
```

Monitor bot resource usage:

```bash
htop -p $(pgrep -f "python bot.py")
```

## 🐛 Troubleshooting

### Bot চালু হচ্ছে না:

```bash
# Logs check করুন
sudo journalctl -u telegram-bot -n 50

# বা
tail -100 /var/log/telegram-bot/error.log
```

### Permission errors:

```bash
# Ownership fix করুন
sudo chown -R $USER:$USER /opt/telegram-bot

# Downloads folder permission
chmod 755 /opt/telegram-bot/downloads
```

### Database locked errors:

```bash
# Database file permission check করুন
ls -la /opt/telegram-bot/*.db

# Fix করুন
chmod 644 /opt/telegram-bot/bot_database.db
```

## 📞 Health Check

Bot running আছে কিনা check করার script:

```bash
nano /opt/telegram-bot/health_check.sh
```

```bash
#!/bin/bash

if systemctl is-active --quiet telegram-bot; then
    echo "✅ Bot is running"
    exit 0
else
    echo "❌ Bot is not running"
    echo "Attempting to restart..."
    sudo systemctl restart telegram-bot
    sleep 5
    if systemctl is-active --quiet telegram-bot; then
        echo "✅ Bot restarted successfully"
    else
        echo "❌ Failed to restart bot"
        # Send alert (optional)
    fi
fi
```

```bash
chmod +x /opt/telegram-bot/health_check.sh
```

Cron job:

```
*/5 * * * * /opt/telegram-bot/health_check.sh >> /var/log/telegram-bot/health.log 2>&1
```

## 🎯 Production Checklist

- [ ] Server updated এবং secured
- [ ] Python এবং dependencies installed
- [ ] .env এবং credentials.json configured
- [ ] Systemd service created এবং running
- [ ] Firewall configured
- [ ] SSL certificate setup (webhook এর জন্য)
- [ ] Automatic backup setup
- [ ] Log rotation configured
- [ ] Health check script setup
- [ ] Monitoring tools installed

## 🔄 Update Process

Bot update করার জন্য:

```bash
cd /opt/telegram-bot
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart telegram-bot
sudo systemctl status telegram-bot
```

---

**Production এ সফলভাবে deploy করার পর bot 24/7 চলবে এবং auto-restart হবে!**
