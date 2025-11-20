# 🚀 Quick Start Guide

Bot দ্রুত চালু করার জন্য এই steps follow করুন:

## ⏱️ ৫ মিনিটে Bot চালু করুন

### Step 1: Python Install করুন (যদি না থাকে)

[Python 3.8+](https://www.python.org/downloads/) ডাউনলোড এবং ইনস্টল করুন।

### Step 2: Dependencies Install করুন

```bash
pip install -r requirements.txt
```

### Step 3: Telegram API Credentials পান

1. [my.telegram.org](https://my.telegram.org) এ যান
2. Phone number দিয়ে login করুন
3. "API development tools" → App তৈরি করুন
4. **API ID** এবং **API Hash** কপি করুন

### Step 4: .env File তৈরি করুন

```bash
# Windows এ:
copy .env.example .env

# Linux/Mac এ:
cp .env.example .env
```

`.env` ফাইল খুলে এই তিনটি পূরণ করুন:

```env
BOT_TOKEN=আপনার_বট_টোকেন_এখানে
API_ID=আপনার_API_ID_এখানে
API_HASH=আপনার_API_HASH_এখানে
ADMIN_IDS=আপনার_ইউজার_আইডি_এখানে
```

**বট টোকেন পেতে:** [@BotFather](https://t.me/BotFather) এ `/newbot` পাঠান

### Step 5: Bot চালান (Google Drive ছাড়াই)

```bash
python bot.py
```

✅ এই পর্যন্ত Bot চালু হয়ে যাবে এবং Telegram এ ছোট ফাইল (২GB পর্যন্ত) আপলোড করতে পারবেন!

---

## 🌟 Google Drive Setup (Optional)

বড় ফাইল আপলোড করতে চাইলে Google Drive configure করুন:

### Step 1: Google Cloud Project তৈরি করুন

1. [console.cloud.google.com](https://console.cloud.google.com/) এ যান
2. "New Project" ক্লিক করুন
3. Project এর নাম দিন → "Create"

### Step 2: Google Drive API Enable করুন

1. Left Menu → "APIs & Services" → "Library"
2. Search: "Google Drive API"
3. "Enable" ক্লিক করুন

### Step 3: OAuth Setup করুন

1. "APIs & Services" → "OAuth consent screen"
2. User Type: **External** → "Create"
3. Fill করুন:
   - App name: আপনার bot এর নাম
   - Support email: আপনার email
   - Developer email: আপনার email
4. "Save and Continue" (3 বার)
5. Scopes page এ → "Add or Remove Scopes"
6. Search: `.../auth/drive.file` → Select → "Update"
7. Test users: আপনার Gmail add করুন
8. "Save and Continue"

### Step 4: Credentials তৈরি করুন

1. "APIs & Services" → "Credentials"
2. "Create Credentials" → "OAuth client ID"
3. Application type: **Desktop app**
4. Name: যেকোনো নাম
5. "Create" → Download JSON
6. JSON file টি `credentials.json` নামে bot folder এ রাখুন

### Step 5: Bot Restart করুন

```bash
python bot.py
```

### Step 6: Google Drive Login করুন

1. Bot এ `/login` পাঠান
2. "Google এ লগইন করুন" বাটন ক্লিক করুন
3. Google account select করুন
4. "Continue" ক্লিক করুন (unsafe app warning দেখলে)
5. "Allow" করুন
6. আবার bot এ `/login` পাঠান

✅ এখন বড় ফাইলও Google Drive এ আপলোড করতে পারবেন!

---

## 🎯 Quick Test

Bot test করার জন্য:

1. Bot এ `/start` পাঠান
2. একটি Direct Download Link পাঠান (যেমন: কোন public file এর direct link)
3. Upload option select করুন
4. Bot ফাইল আপলোড করবে!

### Test Link উদাহরণ:

```
https://speed.hetzner.de/100MB.bin
```

(এটি একটি 100MB test file এর direct link)

---

## ❓ Common Issues

### "Invalid bot token"
- `.env` ফাইলে `BOT_TOKEN` সঠিক আছে কিনা check করুন
- Token এর আগে/পরে extra space নেই তো?

### "Permission denied"
- Bot folder এ write permission আছে কিনা check করুন

### Google Drive login কাজ করছে না
- OAuth Consent Screen এ **Test users** add করেছেন কিনা check করুন
- credentials.json ফাইল bot folder এ আছে কিনা check করুন

---

## 🎓 Next Steps

এখন আপনি:
- `/admin` command দিয়ে Admin Panel দেখুন
- User package change করুন
- Statistics দেখুন
- আরো users add করুন

বিস্তারিত জানতে [README.md](README.md) দেখুন।

---

## 💡 Pro Tips

1. **Testing এর জন্য:** প্রথমে ছোট ফাইল দিয়ে test করুন
2. **Monthly Reset:** প্রতি মাসের ১ তারিখে limit auto reset হয়
3. **Multiple Admins:** `.env` তে comma দিয়ে আলাদা করে admin IDs add করুন
4. **Production Deploy:** VPS/Cloud server এ deploy করলে webhook use করুন

---

**সমস্যার সম্মুখীন হলে README.md এর Troubleshooting section দেখুন!**