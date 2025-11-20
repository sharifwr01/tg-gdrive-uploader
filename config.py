import os
from dotenv import load_dotenv

load_dotenv()

# Admin User IDs (Comma separated in .env file)
ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip()]

# Package limits (in bytes)
# 1 GB = 1024 * 1024 * 1024 bytes
PACKAGES = {
    'free': 1 * 1024 * 1024 * 1024,      # 1 GB
    'basic': 5 * 1024 * 1024 * 1024,     # 5 GB
    'pro': 20 * 1024 * 1024 * 1024,      # 20 GB
    'premium': 50 * 1024 * 1024 * 1024,  # 50 GB
    'unlimited': float('inf')             # Unlimited
}

# Telegram file size limit (2 GB in bytes)
TELEGRAM_FILE_LIMIT = 2 * 1024 * 1024 * 1024

# Download chunk size (1 MB)
DOWNLOAD_CHUNK_SIZE = 1024 * 1024

# Temporary download directory
DOWNLOAD_DIR = 'downloads'

# Database name
DATABASE_NAME = 'bot_database.db'

# Google Drive settings
GOOGLE_CLIENT_SECRETS_FILE = os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'credentials.json')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080/')

# Bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Webhook settings (optional, for production)
USE_WEBHOOK = os.getenv('USE_WEBHOOK', 'False').lower() == 'true'
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
PORT = int(os.getenv('PORT', 8443))