# Telegram File Upload Bot

একটি শক্তিশালী Telegram Bot যা Direct Download Link থেকে ফাইল Telegram এবং Google Drive এ আপলোড করে।

## ✨ ফিচার সমূহ

- 📥 Direct Download Link থেকে ফাইল ডাউনলোড
- 📤 Telegram এ আপলোড (২GB এর কম ফাইলের জন্য)
- ☁️ Google Drive এ আপলোড (যেকোনো সাইজের ফাইলের জন্য)
- 📊 মাসিক আপলোড লিমিট সিস্টেম
- 📦 বিভিন্ন প্যাকেজ সাপোর্ট (Free, Basic, Pro, Premium, Unlimited)
- 👑 Admin Panel
- 🔐 Google Drive OAuth2 Authentication
- 📈 Upload History ও Statistics

## 📋 প্রয়োজনীয় জিনিস

- Python 3.8 বা তার উপরের ভার্সন
- Telegram Bot Token
- Google Cloud Console Account (Google Drive API এর জন্য)

## 🚀 Installation

### 1. Repository Clone করুন

```bash
git clone <repository-url>
cd telegram-file-upload-bot
```

### 2. Virtual Environment তৈরি করুন (Optional কিন্তু সুপারিশকৃত)

```bash
python -m venv venv

# Windows এ:
venv\Scripts\activate

# Linux/Mac এ:
source venv/bin/activate
```

### 3. Dependencies ইনস্টল করুন

```bash
pip install -r requirements.txt
```

## 🔑 Credentials Setup

### 1️⃣ Telegram Bot Token পেতে

1. Telegram এ [@BotFather](https://t.me/BotFather) খুলুন
2. `/newbot` কমান্ড পাঠান
3. আপনার বটের নাম দিন (যেমন: My File Upload Bot)
4. আপনার বটের username দিন (শেষে bot থাকতে হবে, যেমন: myfileuploadbot)
5. BotFather আপনাকে একটি Token দেবে যা দেখতে এরকম:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
6. এই Token কপি করে রাখুন

### 2️⃣ Telegram API ID এবং API Hash পেতে

**⚠️ গুরুত্বপূর্ণ: 2GB পর্যন্ত ফাইল Telegram এ আপলোড করার জন্য API ID ও API Hash প্রয়োজন।**

1. [my.telegram.org](https://my.telegram.org) এ যান
2. আপনার Phone Number দিয়ে লগইন করুন
3. Verification code পাবেন, সেটি দিয়ে verify করুন
4. "API development tools" এ ক্লিক করুন
5. যদি আগে কোন App তৈরি না করে থাকেন, তাহলে:
   - App title: আপনার বটের নাম (যেমন: My Upload Bot)
   - Short name: ছোট নাম (যেমন: mybot)
   - Platform: যেকোনো একটি সিলেক্ট করুন (Android/iOS/Desktop)
   - "Create application" ক্লিক করুন
6. আপনি **api_id** এবং **api_hash** পাবেন
7. এই দুটি কপি করে সংরক্ষণ করুন

**উদাহরণ:**
```
api_id: 12345678
api_hash: 0123456789abcdef0123456789abcdef
```

### 3️⃣ Admin User ID পেতে

1. Telegram এ [@userinfobot](https://t.me/userinfobot) বট খুলুন
2. `/start` পাঠান
3. বট আপনার User ID দেখাবে (যেমন: 123456789)
4. এই ID কপি করে রাখুন
5. একাধিক Admin থাকলে সবার ID কমা দিয়ে আলাদা করুন

### 3️⃣ Google Drive API Credentials পেতে

#### Step 1: Google Cloud Project তৈরি করুন

1. [Google Cloud Console](https://console.cloud.google.com/) এ যান
2. নতুন Project তৈরি করুন:
   - উপরে "Select a project" এ ক্লিক করুন
   - "New Project" এ ক্লিক করুন
   - Project এর নাম দিন (যেমন: Telegram File Bot)
   - "Create" এ ক্লিক করুন

#### Step 2: Google Drive API Enable করুন

1. Left sidebar থেকে "APIs & Services" > "Library" এ যান
2. সার্চ বক্সে "Google Drive API" লিখুন
3. "Google Drive API" সিলেক্ট করুন
4. "Enable" বাটনে ক্লিক করুন

#### Step 3: OAuth Consent Screen Configure করুন

1. "APIs & Services" > "OAuth consent screen" এ যান
2. User Type: "External" সিলেক্ট করুন, তারপর "Create"
3. App Information পূরণ করুন:
   - App name: আপনার বটের নাম
   - User support email: আপনার email
   - Developer contact: আপনার email
4. "Save and Continue" ক্লিক করুন
5. Scopes page এ "Add or Remove Scopes" ক্লিক করুন
6. সার্চ করুন: `https://www.googleapis.com/auth/drive.file`
7. চেকবক্স টিক করে "Update" এবং "Save and Continue"
8. Test users: আপনার Gmail address যোগ করুন
9. "Save and Continue" ক্লিক করুন

#### Step 4: OAuth 2.0 Credentials তৈরি করুন

1. "APIs & Services" > "Credentials" এ যান
2. "Create Credentials" > "OAuth client ID" ক্লিক করুন
3. Application type: "Desktop app" সিলেক্ট করুন
4. Name: যেকোনো নাম দিন (যেমন: Bot Desktop Client)
5. "Create" ক্লিক করুন
6. Download JSON বাটনে ক্লিক করে credentials.json ফাইল ডাউনলোড করুন
7. এই ফাইলটি আপনার bot folder এ রাখুন

## ⚙️ Configuration

### 1. .env ফাইল তৈরি করুন

`.env.example` ফাইলটি কপি করে `.env` নামে সেভ করুন:

```bash
cp .env.example .env
```

### 2. .env ফাইল এডিট করুন

```env
# Telegram Bot Token (BotFather থেকে পাওয়া)
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Telegram API Credentials (my.telegram.org থেকে পাওয়া)
API_ID=12345678
API_HASH=0123456789abcdef0123456789abcdef

# Admin User IDs (কমা দিয়ে আলাদা)
ADMIN_IDS=123456789,987654321

# Google Drive Credentials File
GOOGLE_CLIENT_SECRETS_FILE=credentials.json

# Redirect URI (default রাখুন)
REDIRECT_URI=http://localhost:8080/

# Optional: Webhook (production এর জন্য)
USE_WEBHOOK=False
WEBHOOK_URL=
PORT=8443
```

### 3. credentials.json ফাইল

Google Cloud Console থেকে ডাউনলোড করা `credentials.json` ফাইলটি bot folder এ রাখুন।

## 🎮 Bot চালানো

```bash
python bot.py
```

Bot সফলভাবে চালু হলে দেখবেন:
```
INFO - Bot started!
```

## 📱 Bot ব্যবহার করা

### ইউজার কমান্ড সমূহ:

- `/start` - বট শুরু করুন
- `/help` - সাহায্য দেখুন
- `/status` - আপনার লিমিট ও স্ট্যাটাস দেখুন
- `/login` - Google Drive এ লগইন করুন
- `/logout` - Google Drive থেকে লগআউট করুন

### Admin কমান্ড:

- `/admin` - Admin Panel খুলুন

### ফাইল আপলোড করা:

1. একটি Direct Download Link পাঠান
2. Bot ফাইল সাইজ চেক করবে
3. আপলোড অপশন দেখাবে (Telegram/Google Drive)
4. আপনার পছন্দ সিলেক্ট করুন
5. Bot ফাইল আপলোড করবে

## 📦 Package System

বটে 5 টি প্যাকেজ আছে:

| Package | Monthly Limit |
|---------|---------------|
| Free | 1 GB |
| Basic | 5 GB |
| Pro | 20 GB |
| Premium | 50 GB |
| Unlimited | সীমাহীন |

Admin প্যানেল থেকে ইউজারদের প্যাকেজ পরিবর্তন করা যায়।

## 🔧 File Structure

```
telegram-file-upload-bot/
│
├── bot.py                  # Main bot file
├── database.py            # Database handler
├── google_drive.py        # Google Drive uploader
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (তৈরি করতে হবে)
├── .env.example          # Environment variables example
├── credentials.json      # Google OAuth credentials (তৈরি করতে হবে)
├── bot_database.db       # SQLite database (auto-created)
└── downloads/            # Temporary download folder (auto-created)
```

## 🔐 Security Notes

1. `.env` এবং `credentials.json` ফাইল **কখনো** public repository তে আপলোড করবেন না
2. `.gitignore` ফাইলে এগুলো যোগ করুন:
   ```
   .env
   credentials.json
   bot_database.db
   downloads/
   *.pyc
   __pycache__/
   venv/
   ```
3. Bot token এবং credentials সুরক্ষিত রাখুন
4. শুধুমাত্র বিশ্বস্ত ব্যক্তিদের Admin করুন

## 🐛 Troubleshooting

### Bot শুরু হচ্ছে না:

1. `.env` ফাইল সঠিকভাবে configured আছে কিনা চেক করুন
2. Bot Token সঠিক আছে কিনা চেক করুন
3. Internet connection চেক করুন

### Google Drive login কাজ করছে না:

1. Google Drive API enable করা আছে কিনা চেক করুন
2. OAuth Consent Screen configure করা আছে কিনা চেক করুন
3. credentials.json ফাইল সঠিক জায়গায় আছে কিনা চেক করুন
4. Test users list এ আপনার email add করা আছে কিনা চেক করুন

### File upload fail হচ্ছে:

1. Direct Download Link সঠিক আছে কিনা চেক করুন
2. Monthly limit শেষ হয়ে গেছে কিনা `/status` দিয়ে চেক করুন
3. Internet connection stable আছে কিনা চেক করুন

## 📞 Support

সমস্যার সম্মুখীন হলে:

1. Error message সাবধানে পড়ুন
2. Troubleshooting section চেক করুন
3. Log messages দেখুন

## 📝 License

MIT License

## 🙏 Credits

Made with ❤️ using Python and Telegram Bot API