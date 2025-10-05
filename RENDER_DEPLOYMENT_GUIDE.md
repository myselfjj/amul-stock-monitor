# 🟦 Render.com Deployment Guide - Amul Stock Monitor with Telegram Bot

## 🎯 **Why Render.com?**

✅ **Free Tier** - 750 hours/month (enough for 24/7)  
✅ **No Credit Card** required for free tier  
✅ **Auto-deploy** from GitHub  
✅ **Better than Railway** - Railway now requires paid plan  
✅ **Built-in HTTPS** and health checks  

---

## 📋 **Pre-Deployment Checklist**

### ✅ **What You Need:**
1. **GitHub Account** (free)
2. **Render.com Account** (free - no credit card needed)
3. **Telegram Bot Token** (free)
4. **Your Telegram User ID** (free)
5. **Gmail App Password** (for email notifications)

---

## 🤖 **Step 1: Create Telegram Bot (5 minutes)**

### **1.1 Create Bot:**
1. Open Telegram → Search **@BotFather**
2. Send: `/newbot`
3. Bot name: **"Amul Stock Monitor"**
4. Username: **"your_amul_monitor_bot"** (must end with 'bot')
5. **Copy your TOKEN**: `123456789:ABCdefGHIjklMNOp-qRSTuvwxyz`

### **1.2 Get Your User ID:**
1. Search **@userinfobot** in Telegram
2. Send: `/start`
3. **Copy your User ID**: `123456789`

💡 **Tip**: If you want multiple users to control the bot, get all their User IDs and you'll add them as comma-separated values like: `123456789,987654321`

---

## 📂 **Step 2: Setup GitHub Repository (3 minutes)**

### **2.1 Initialize Git (if not already done):**
```bash
cd /Users/jayesh.jadhav/Documents/Personal/amul-stock-monitor

# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit: Amul Stock Monitor with Telegram Bot"
```

### **2.2 Create GitHub Repository:**
1. Go to: https://github.com/new
2. Repository name: **amul-stock-monitor**
3. Keep it **Private** (recommended)
4. Click **"Create repository"**

### **2.3 Push to GitHub:**
```bash
# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/amul-stock-monitor.git

# Push your code
git branch -M main
git push -u origin main
```

---

## ☁️ **Step 3: Deploy to Render.com (5 minutes)**

### **3.1 Create Render Account:**
1. Go to: https://render.com/
2. Click **"Get Started"**
3. Sign up with **GitHub** (recommended)
4. Authorize Render to access your repositories

### **3.2 Create New Web Service:**
1. Click **"New +"** → **"Web Service"**
2. Select **"Build and deploy from a Git repository"**
3. Click **"Connect account"** (if not already connected)
4. Find and select your **amul-stock-monitor** repository
5. Click **"Connect"**

### **3.3 Configure Service:**

Fill in these settings:

| **Field** | **Value** |
|-----------|-----------|
| **Name** | `amul-stock-monitor` |
| **Region** | `Oregon (US West)` or `Singapore` (closer to India) |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Environment** | `Docker` |
| **Plan** | `Free` |

### **3.4 Add Environment Variables:**

Scroll down to **"Environment Variables"** section and add these:

| **Key** | **Value** | **Notes** |
|---------|-----------|-----------|
| `TELEGRAM_BOT_TOKEN` | `123456789:ABCdefGHIjklMNOp-qRSTuvwxyz` | Your bot token from BotFather |
| `TELEGRAM_AUTHORIZED_USERS` | `123456789` | Your user ID from userinfobot |
| `PORT` | `5000` | Required for Render |
| `PYTHONUNBUFFERED` | `1` | Better logging |

💡 **Important**: Replace the example values with YOUR actual bot token and user ID!

### **3.5 Deploy:**
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for the first deployment (Render builds the Docker container)
3. Watch the logs for deployment progress

---

## 🎯 **Step 4: Verify Deployment (3 minutes)**

### **4.1 Check Deployment Status:**
In Render Dashboard:
- Look for **"Deploy succeeded"** message
- Status should show **"Live"** (green)

### **4.2 Check Logs:**
Click **"Logs"** tab and look for these messages:
```
✅ 🚀 Self-Contained Amul Stock Monitor has started.
✅ Flask health endpoint running on port 5000
✅ 🤖 Telegram Bot Controller started successfully!
✅ Setting pincode 500018 for this session...
✅ [timestamp] Checking: product-name
```

### **4.3 Test Health Endpoint:**
1. Copy your Render URL (looks like: `https://amul-stock-monitor.onrender.com`)
2. Open in browser: `https://amul-stock-monitor.onrender.com/health`
3. You should see: `{"status": "healthy", "service": "amul-stock-monitor"}`

---

## 🤖 **Step 5: Test Telegram Bot (2 minutes)**

### **5.1 Find Your Bot:**
1. Open Telegram
2. Search for your bot: **@your_amul_monitor_bot**
3. Click **"Start"** or send: `/start`

### **5.2 Expected Response:**
```
🤖 Amul Stock Monitor Controller

🎯 Monitor Status: ACTIVE
📦 Products: Checking every cycle  
📧 Emails: Ready to send alerts

Use buttons below for full control:

[📊 View Status] [📦 Manage Products]
[📧 Manage Emails] [📍 Change Pincode]
[⏰ Change Interval] [🔄 Manual Check]
```

### **5.3 Test Bot Features:**
1. Click **"📊 View Status"** → See your configuration
2. Click **"🔄 Manual Check"** → Trigger immediate stock check
3. Check your email for any stock alerts

---

## 🎛️ **Bot Control Features**

### **📦 Manage Products:**
- **View**: See all monitored products
- **Add**: Add new products (3-step process: name, URL, price)
- **Remove**: Remove products you no longer want to monitor

### **📧 Manage Emails:**
- **View**: See all recipient emails
- **Add**: Add new email recipients
- **Remove**: Remove email recipients

### **📍 Change Pincode:**
- Update delivery pincode for stock checks
- Supports all Indian 6-digit pincodes

### **⏰ Change Interval:**
- **5 minutes**: Faster alerts, more resource usage
- **10 minutes**: Balanced (recommended)
- **15 minutes**: Slower, less resource usage

### **🔄 Manual Check:**
- Trigger immediate stock check for all products
- Useful for testing or when you need instant updates

---

## 📊 **Monitor Your System**

### **Render Dashboard Monitoring:**
1. **Metrics tab**: View CPU, Memory, Network usage
2. **Logs tab**: Real-time application logs
3. **Events tab**: Deployment history

### **Expected Resource Usage:**
- **CPU**: 5-15% (spikes during checks)
- **Memory**: 200-500MB
- **Build Time**: 5-10 minutes (first time), 2-3 minutes (updates)

### **Health Check:**
Your service URL: `https://amul-stock-monitor.onrender.com/health`
- Should return: `{"status": "healthy", "service": "amul-stock-monitor"}`

---

## 🔧 **Troubleshooting**

### **Problem: Bot Not Responding**
**Solutions:**
1. Check Render logs for errors
2. Verify `TELEGRAM_BOT_TOKEN` is correct
3. Verify `TELEGRAM_AUTHORIZED_USERS` contains your user ID
4. Check if service is "Live" in Render dashboard

### **Problem: "Unauthorized access!"**
**Solutions:**
1. Your Telegram User ID is not in `TELEGRAM_AUTHORIZED_USERS`
2. Get your ID again from @userinfobot
3. Update environment variable in Render
4. Restart the service

### **Problem: Emails Not Sending**
**Solutions:**
1. Check `email_config.json` has correct Gmail credentials
2. Use Gmail App Password (not regular password)
3. Check recipient email addresses are valid
4. Look for email errors in Render logs

### **Problem: Stock Checks Failing**
**Solutions:**
1. Check Render logs for ChromeDriver errors
2. Verify pincode is valid 6-digit Indian pincode
3. Check product URLs are accessible
4. System usually auto-recovers from temporary failures

### **Problem: Service Keeps Sleeping**
**Note:** Render free tier spins down after 15 minutes of inactivity
**Solutions:**
1. The Flask health endpoint keeps it awake
2. Regular monitoring checks prevent sleep
3. If it sleeps, it will wake up automatically on next check
4. Consider upgrading to paid plan ($7/month) for 24/7 guarantee

---

## 🔄 **Updating Your Deployment**

### **Method 1: Via GitHub (Recommended)**
```bash
# Make changes to your code
git add .
git commit -m "Update configuration"
git push

# Render will auto-deploy in 2-3 minutes
```

### **Method 2: Via Telegram Bot**
- Most settings can be changed via Telegram bot
- No need to redeploy!
- Changes are instant

### **Method 3: Manual Redeploy**
1. Go to Render Dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 💰 **Cost Comparison**

| **Platform** | **Free Tier** | **24/7 Uptime** | **Credit Card Required** |
|--------------|---------------|-----------------|--------------------------|
| **Render** ✅ | 750 hrs/month | Yes (with caveats*) | No |
| **Railway** ❌ | None (paid only) | Yes | Yes |
| **Heroku** | Discontinued | - | - |
| **Fly.io** | Limited | Yes | Yes |

*Render free tier may spin down after 15 min inactivity, but wakes up automatically.

### **Render Paid Plan ($7/month):**
- ✅ True 24/7 uptime (no spin down)
- ✅ More resources
- ✅ Faster build times
- ✅ Priority support

---

## 📱 **Daily Usage**

### **Morning Routine:**
1. Open Telegram → Start your bot
2. Click **"📊 View Status"** → Verify system is running
3. Check your email for any overnight stock alerts

### **Adding New Products:**
1. Bot → **"📦 Manage Products"** → **"➕ Add New Product"**
2. Follow the 3-step wizard
3. Bot will immediately check the new product

### **Emergency Manual Check:**
1. Bot → **"🔄 Manual Check"**
2. Wait ~2 minutes for results
3. Check email for alerts

---

## 🎉 **Success Checklist**

### **✅ Deployment Successful When:**
- [ ] Render shows "Live" status
- [ ] Health endpoint returns success
- [ ] Bot responds to `/start` command
- [ ] Logs show monitoring cycles every 10 minutes
- [ ] Manual check works and completes

### **✅ System Working When:**
- [ ] Regular checks appear in logs
- [ ] Email notifications received (when products in stock)
- [ ] Bot allows adding/removing products and emails
- [ ] Configuration changes via bot persist after restart

---

## 🚨 **Quick Reference**

### **Service URL:**
```
https://amul-stock-monitor.onrender.com
```

### **Health Check:**
```
https://amul-stock-monitor.onrender.com/health
```

### **Telegram Bot Commands:**
```
/start - Show main menu
```

### **Render Dashboard:**
```
https://dashboard.render.com/
```

---

## 🔐 **Security Best Practices**

✅ **Keep repository private** on GitHub  
✅ **Don't commit secrets** to Git (use environment variables)  
✅ **Use Gmail App Passwords** (not regular password)  
✅ **Limit authorized Telegram users** to yourself or trusted people  
✅ **Regularly check Render logs** for suspicious activity  

---

## 🎊 **You're All Set!**

Your Amul Stock Monitor is now:
- ✅ Running 24/7 on Render.com
- ✅ Checking products every 10 minutes
- ✅ Sending email alerts when stock is available
- ✅ Fully controllable via Telegram bot
- ✅ Completely free (with Render free tier)

**Need help?** Check Render logs or test features via the Telegram bot!

---

**Questions or Issues?**  
1. Check Render logs first
2. Verify environment variables
3. Test bot with `/start` command
4. Review this guide's troubleshooting section
