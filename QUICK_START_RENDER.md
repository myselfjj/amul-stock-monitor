# ⚡ Quick Start - Deploy to Render in 10 Minutes

## 📝 **Pre-Flight Checklist**

### **1️⃣ Get Telegram Bot Token (2 min)**
```
1. Open Telegram → Search: @BotFather
2. Send: /newbot
3. Name: Amul Stock Monitor
4. Username: your_amul_monitor_bot
5. COPY TOKEN: 123456789:ABCdefGHI...
```

### **2️⃣ Get Your Telegram User ID (1 min)**
```
1. Search: @userinfobot
2. Send: /start  
3. COPY YOUR ID: 123456789
```

### **3️⃣ Push to GitHub (2 min)**
```bash
cd /Users/jayesh.jadhav/Documents/Personal/amul-stock-monitor

# If not initialized:
git init
git add .
git commit -m "Deploy to Render"

# Create repo on github.com/new → Copy commands:
git remote add origin https://github.com/YOUR_USERNAME/amul-stock-monitor.git
git branch -M main
git push -u origin main
```

---

## 🚀 **Deploy to Render (5 min)**

### **Step 1: Create Account**
1. Go to: **render.com**
2. Sign up with **GitHub**

### **Step 2: New Web Service**
1. Click **"New +"** → **"Web Service"**
2. Connect your **amul-stock-monitor** repo
3. Click **"Connect"**

### **Step 3: Configure**
| Setting | Value |
|---------|-------|
| Name | `amul-stock-monitor` |
| Region | `Oregon` or `Singapore` |
| Branch | `main` |
| Environment | `Docker` |
| Plan | `Free` |

### **Step 4: Environment Variables**
Add these in "Environment Variables" section:

```
TELEGRAM_BOT_TOKEN = <YOUR_BOT_TOKEN_FROM_BOTFATHER>
TELEGRAM_AUTHORIZED_USERS = <YOUR_USER_ID_FROM_USERINFOBOT>
PORT = 5000
PYTHONUNBUFFERED = 1
```

### **Step 5: Deploy**
1. Click **"Create Web Service"**
2. Wait 5-10 minutes
3. Look for **"Deploy succeeded"** ✅

---

## ✅ **Test (2 min)**

### **1. Check Health**
Open: `https://amul-stock-monitor.onrender.com/health`  
Should see: `{"status": "healthy", "service": "amul-stock-monitor"}`

### **2. Test Bot**
1. Open Telegram
2. Search: `@your_amul_monitor_bot`
3. Send: `/start`
4. Should see menu with buttons ✅

### **3. Trigger Check**
1. Click **"🔄 Manual Check"**
2. Wait 2 minutes
3. Check email for any alerts

---

## 🎯 **You're Done!**

Your monitor is now:
- ✅ Running 24/7 on Render (free)
- ✅ Checking stock every 10 minutes
- ✅ Sending email alerts
- ✅ Controlled via Telegram bot

---

## 📱 **Quick Commands**

### **Add Product:**
Bot → Manage Products → Add New Product → Follow wizard

### **Change Interval:**
Bot → Change Interval → Pick 5/10/15 minutes

### **Add Email:**
Bot → Manage Emails → Add New Email → Enter address

### **Manual Check:**
Bot → Manual Check → Wait for results

---

## 🔧 **Need Help?**

**Bot not responding?**
- Check Render logs for errors
- Verify environment variables are set
- Make sure service status is "Live"

**Emails not working?**
- Check `email_config.json` has Gmail app password
- Verify recipient emails are correct

**Service sleeping?**
- Normal for free tier after 15 min inactivity
- Wakes up automatically on next check
- Flask endpoint keeps it mostly awake

---

## 📚 **Full Documentation**

For detailed guides, see:
- `RENDER_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `TELEGRAM_BOT_SETUP.md` - Telegram bot features
- `DEPLOYMENT_GUIDE.md` - General deployment info

---

**🎉 Enjoy your automated Amul stock alerts!**
