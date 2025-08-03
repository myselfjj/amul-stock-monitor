# 🤖 Telegram Bot Controller Setup Guide

## 🎯 **What You Get**

Your Telegram bot will let you:
- ✅ **Add/Remove products** instantly
- ✅ **Add/Remove email addresses** 
- ✅ **Change monitoring intervals** (5, 10, 15 mins)
- ✅ **Change pincode** for different cities
- ✅ **Trigger manual checks** 
- ✅ **View current status** of all settings
- ✅ **Secure access** - only authorized users

---

## 🚀 **Setup Steps**

### **Step 1: Create Your Telegram Bot**

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send:** `/newbot`
4. **Choose a name:** `Amul Stock Monitor Bot`
5. **Choose a username:** `your_amul_monitor_bot` (must end with 'bot')
6. **Copy the bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrSTUvwxyz`)

### **Step 2: Get Your Telegram User ID**

1. **Search for:** `@userinfobot` in Telegram
2. **Start the bot** and it will show your user ID
3. **Copy your user ID** (numbers like: `123456789`)

### **Step 3: Configure the Bot**

Edit `telegram_bot.py` and update these lines:

```python
# Line 275-276: Add your bot token and user ID
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxyz"  # From BotFather
AUTHORIZED_USERS = [123456789]  # Your user ID from userinfobot
```

### **Step 4: Test Locally (Optional)**

```bash
# Install telegram dependency
pip3 install python-telegram-bot==20.7

# Run the bot
python3 telegram_bot.py
```

### **Step 5: Deploy to Railway**

Upload these files to GitHub:
- ✅ `telegram_bot.py` (configured with your token)
- ✅ `amul_email_monitor.py` (main monitor)
- ✅ `requirements.txt` (updated with telegram)
- ✅ `email_config.json` (your config)

---

## 🔧 **Bot Commands**

Once deployed, message your bot:

### **/start** - Main Menu
Shows all available options:
- 📦 Manage Products
- 📧 Manage Emails  
- ⏰ Manage Settings
- 📊 View Status
- 🔄 Manual Check

---

## 📱 **Usage Examples**

### **Add New Product:**
1. Tap "📦 Manage Products"
2. Tap "➕ Add New Product"
3. Send the Amul product URL
4. Bot automatically extracts name and price

### **Change Check Interval:**
1. Tap "⏰ Manage Settings"
2. Choose your preferred interval:
   - 🔄 5 minutes (faster alerts, higher cost)
   - 🔄 10 minutes (balanced)
   - 🔄 15 minutes (slower, lower cost)

### **Add Email Recipient:**
1. Tap "📧 Manage Emails"
2. Tap "➕ Add New Email"
3. Send the email address
4. Bot validates and adds it

### **Manual Stock Check:**
1. Tap "🔄 Manual Check"
2. Bot immediately checks all products
3. You get status update in ~2 minutes

---

## 🔒 **Security Features**

✅ **Authorized Users Only**: Only your Telegram ID can control the bot  
✅ **No Public Access**: Bot ignores commands from other users  
✅ **Secure Token**: Bot token stays in your Railway environment  
✅ **Safe Operations**: All config changes are validated  

---

## 🚀 **Deployment Options**

### **Option A: Run Both Services**
Run both the monitor AND bot together:
```python
# In main script, add:
bot_thread = Thread(target=run_telegram_bot)
bot_thread.start()
```

### **Option B: Separate Services** (Recommended)
- **Service 1**: Amul Monitor (main monitoring)
- **Service 2**: Telegram Bot (configuration control)

Both share the same `email_config.json` file.

---

## 💰 **Cost Impact**

**Telegram Bot**: Almost no additional cost!
- ✅ **Minimal resources**: Only responds to commands
- ✅ **Event-driven**: No continuous polling
- ✅ **Lightweight**: ~10MB RAM when idle

**Total estimated cost remains**: ~$8-12/month on Railway

---

## 🎉 **What You'll Love**

🤖 **Instant Control**: Change settings from anywhere  
📱 **Mobile Friendly**: Perfect for on-the-go management  
⚡ **Real-time Updates**: See changes immediately  
🔔 **Notifications**: Bot confirms all changes  
🛡️ **Secure**: Only you can control your monitor  

---

## 🔧 **Ready to Deploy?**

1. ✅ **Get bot token** from @BotFather
2. ✅ **Get your user ID** from @userinfobot  
3. ✅ **Update telegram_bot.py** with your details
4. ✅ **Upload to GitHub** and deploy to Railway
5. ✅ **Message your bot** with /start

**You'll have full remote control of your stock monitor!** 🎊
