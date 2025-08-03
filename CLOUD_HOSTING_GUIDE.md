# 🌐 Amul Stock Monitor - Cloud Hosting Guide

## 🚀 **Deploy to Railway (Recommended)**

### **Why Railway?**
✅ **$5/month free credit** (enough for this app)  
✅ **Auto-deployment** from GitHub  
✅ **Built-in Chrome** support  
✅ **24/7 uptime** guaranteed  
✅ **Automatic restarts** on failures  

### **Step-by-Step Deployment:**

#### 1. **Prepare Your Repository**
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial Amul Stock Monitor"

# Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/amul-stock-monitor.git
git push -u origin main
```

#### 2. **Deploy to Railway**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select your `amul-stock-monitor` repository
5. Railway will automatically detect and deploy!

#### 3. **Configure Environment (Optional)**
If you want to use environment variables instead of `email_config.json`:
- In Railway dashboard → Settings → Variables
- Add the variables from `.env.example`

#### 4. **Monitor Deployment**
- Check logs in Railway dashboard
- Your app will start automatically
- Monitor every 10 minutes 24/7!

---

## 🟦 **Alternative: Deploy to Render**

### **Step-by-Step:**

#### 1. **Create render.yaml**
Already included in your project!

#### 2. **Deploy**
1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Select "Web Service"
4. Use existing `Dockerfile`
5. Deploy!

---

## 🟨 **Alternative: PythonAnywhere**

### **Step-by-Step:**

#### 1. **Upload Files**
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Create account (free tier available)
3. Upload all project files to `/home/yourusername/`

#### 2. **Install Dependencies**
```bash
# In PythonAnywhere console
pip3.10 install --user -r requirements.txt
```

#### 3. **Create Always-On Task**
1. Go to Dashboard → Tasks
2. Create new task
3. Command: `python3.10 /home/yourusername/amul_email_monitor.py`
4. Enable "Always-on"

---

## 🐳 **Alternative: Any Docker Host**

Your project includes a `Dockerfile` that works on:
- **DigitalOcean App Platform**
- **Google Cloud Run**
- **AWS ECS/Fargate**
- **Azure Container Instances**

### **Generic Docker Deployment:**
```bash
# Build image
docker build -t amul-monitor .

# Run container
docker run -d --name amul-monitor amul-monitor
```

---

## 📊 **Cost Comparison**

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Railway** | $5/month credit | $5-10/month | Easiest setup |
| **Render** | 750 hours/month | $7/month | Good free tier |
| **PythonAnywhere** | Limited hours | $5/month | Python-focused |
| **DigitalOcean** | None | $5/month | Full control |

---

## 🎯 **Recommended: Railway**

**Railway is the easiest and most reliable option for your use case:**

1. 🚀 **5-minute setup** from GitHub
2. 💰 **Free for your needs** ($5 credit lasts months)
3. 🔄 **Auto-restarts** if anything fails
4. 📊 **Built-in monitoring** and logs
5. 🌐 **Always online** - true 24/7 operation

**Your monitor will run independently in the cloud, sending email alerts automatically!** 🎉

---

## 🔧 **Files Ready for Deployment:**

✅ `Dockerfile` - Container configuration  
✅ `railway.json` - Railway deployment settings  
✅ `requirements.txt` - Python dependencies  
✅ `amul_email_monitor.py` - Your headless monitor  
✅ `email_config.json` - Email configuration  
✅ `.env.example` - Environment variables template  

**Just push to GitHub and deploy to Railway - it's that simple!** 🚀
