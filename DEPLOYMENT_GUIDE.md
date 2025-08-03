# 🚀 Complete Deployment Guide - Amul Stock Monitor

## 📋 **Pre-Deployment Checklist**

### ✅ **Files Ready:**
- `amul_email_monitor.py` - Main script with Telegram bot
- `email_config.json` - Configuration file  
- `requirements.txt` - Dependencies
- `railway.json` - Railway deployment config
- `Dockerfile` - Container configuration

### ✅ **What You Need:**
1. **GitHub Account** (free)
2. **Railway Account** (free $5 credit)
3. **Telegram Bot Token** (free)
4. **Your Telegram User ID** (free)

---

## 🤖 **Step 1: Create Telegram Bot (5 minutes)**

### **1.1 Create Bot:**
```
1. Open Telegram → Search "@BotFather"
2. Send: /newbot
3. Bot name: "Amul Stock Monitor"  
4. Username: "your_amul_monitor_bot" (must end with 'bot')
5. Copy your TOKEN: 123456789:ABCdefGHIjklMNOp-qRSTuvwxyz
```

### **1.2 Get Your User ID:**
```
1. Search "@userinfobot" in Telegram
2. Send: /start
3. Copy your User ID: 123456789
```

---

## 📂 **Step 2: Setup GitHub Repository (3 minutes)**

### **2.1 Create Repository:**
```bash
# In your project folder:
git init
git add .
git commit -m "Complete Amul Stock Monitor with Telegram Bot"

# Create repo on GitHub.com → Copy the commands:
git remote add origin https://github.com/yourusername/amul-monitor.git
git branch -M main
git push -u origin main
```

---

## ☁️ **Step 3: Deploy to Railway (5 minutes)**

### **3.1 Connect Railway:**
```
1. Go to: https://railway.app/
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your "amul-monitor" repository
5. Click "Deploy"
```

### **3.2 Configure Environment Variables:**
```
In Railway Dashboard → Your Project → Variables:

Add these variables:
- TELEGRAM_BOT_TOKEN: 123456789:ABCdefGHIjklMNOp-qRSTuvwxyz
- TELEGRAM_AUTHORIZED_USERS: 123456789
- PORT: 5000
```

### **3.3 Monitor Deployment:**
```
Railway Dashboard → Deployments tab:
- Wait for "✅ SUCCESS" status
- Click "View Logs" to see startup
```

---

## 🎯 **Step 4: Test Your Bot (2 minutes)**

### **4.1 Find Your Bot:**
```
1. Open Telegram
2. Search: your_amul_monitor_bot
3. Send: /start
```

### **4.2 Expected Response:**
```
🤖 Amul Stock Monitor Controller

🎯 Monitor Status: ACTIVE
📦 Products: Checking every cycle  
📧 Emails: Ready to send alerts

[📊 View Status] [📦 Manage Products]
[📧 Manage Emails] [⏰ Change Interval]
```

### **4.3 Test Features:**
```
✅ Click "📊 View Status" → See your config
✅ Click "📧 Manage Emails" → Add/remove emails  
✅ Click "📦 Manage Products" → Add/remove products
✅ Click "🔄 Manual Check" → Trigger immediate check
```

---

## 📊 **Step 5: Monitor Your System**

### **5.1 Railway Dashboard:**
```
Metrics tab:
- CPU usage: Should be low (~10-20%)
- Memory: Should be ~200-400MB
- Network: Periodic spikes during checks
```

### **5.2 Check Logs:**
```
Deployments → View Logs:
Look for:
✅ "🤖 Telegram Bot Controller started!"
✅ "Flask health endpoint running on port 5000"  
✅ "✅ Pincode has been set for this session!"
✅ "[timestamp] Checking: product-name"
```

### **5.3 Email Test:**
```
1. Use bot to trigger manual check
2. Check your email for alerts  
3. Verify all recipients receive emails
```

---

## 💰 **Cost Estimates**

### **Railway Pricing:**
| **Interval** | **Monthly Cost** | **Checks/Day** |
|---|---|---|
| 5 minutes | $15-20 | 288 checks |
| 10 minutes | $8-12 | 144 checks |
| 15 minutes | $5-8 | 96 checks |

### **Free Credits:**
- Railway: $5/month free credit
- First month likely FREE with 10-15 min intervals

---

## 🔧 **Troubleshooting**

### **Bot Not Responding:**
```bash
Check Railway logs for:
- "❌ Unauthorized access!" → Wrong user ID
- Import errors → Dependencies issue
- Token errors → Wrong bot token
```

### **Email Not Working:**
```bash
Check email_config.json:
- sender_email: Your Gmail address
- sender_password: App password (not regular password)
- recipient_emails: Valid email addresses
```

### **Stock Check Failing:**
```bash
Check logs for:
- ChromeDriver errors → Usually auto-resolves
- Pincode issues → Verify 6-digit Indian pincode
- Network timeouts → Normal, system retries
```

---

## 🎉 **Success Criteria**

### **✅ Deployment Successful When:**
1. Railway shows "✅ SUCCESS" status
2. Bot responds to `/start` command
3. Manual check works via bot
4. View status shows your products/emails
5. Logs show regular monitoring cycles

### **✅ System Working When:**
1. Regular checks every 10 minutes in logs
2. Email notifications received (if products in stock)
3. Bot allows you to add/remove products/emails
4. Changes via bot are saved and persist

---

## 📱 **Daily Usage**

### **Monitor via Telegram:**
```
Morning: /start → View Status (check system health)
As needed: Add new products, emails, change settings
Emergency: Manual check if needed
```

### **Email Alerts:**
```
You'll receive emails ONLY when:
- Products come back IN STOCK
- After being OUT OF STOCK previously
- Maximum 1 email per product per cooldown period
```

---

## 🚨 **Emergency Commands**

### **Restart System:**
```
Railway Dashboard → Deployments → 3 dots → Redeploy
```

### **Check System Status:**
```
Telegram bot → /start → Manual Check
```

### **Update Configuration:**
```
Use Telegram bot → No need to touch server!
```

---

**🎊 Congratulations! Your Amul Stock Monitor is now deployed and running 24/7 with complete Telegram control!**

**Need help? Check Railway logs or use the Telegram bot's status features to diagnose issues.**
