# 🚀 Amul Stock Monitor - Server Deployment Guide

## ✅ Ready for 24/7 Server Deployment!

Your Amul Stock Monitor is now fully optimized for headless server deployment with multiple email recipients and professional logging.

---

## 📋 **What's Included**

### Core Files:
- `amul_email_monitor.py` - Main monitor script (headless-enabled)
- `email_config.json` - Configuration with multiple recipients
- `requirements.txt` - Python dependencies
- `start_monitor.sh` - Server startup script
- `amul-monitor.service` - Systemd service file for Linux

### Generated Files:
- `amul_monitor.log` - Application logs
- `monitor_output.log` - System output logs

---

## 🎯 **Key Features**

✅ **Headless Operation** - Runs without visible browser  
✅ **Multiple Email Recipients** - Supports arrays of email addresses  
✅ **Professional Logging** - File + console logging with timestamps  
✅ **Server Optimized** - Memory and performance optimizations  
✅ **Auto-Recovery** - Handles errors gracefully  
✅ **24/7 Monitoring** - Continuous operation every 10 minutes  

---

## 🖥️ **Server Deployment Options**

### Option 1: Quick Start (Linux/Mac)
```bash
# Make startup script executable
chmod +x start_monitor.sh

# Start in background
./start_monitor.sh
```

### Option 2: Manual Start
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run in background with logging
nohup python3 amul_email_monitor.py > monitor_output.log 2>&1 &
```

### Option 3: Systemd Service (Linux)
```bash
# Copy service file to systemd
sudo cp amul-monitor.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable amul-monitor
sudo systemctl start amul-monitor

# Check status
sudo systemctl status amul-monitor
```

---

## ⚙️ **Configuration**

### Email Recipients (email_config.json):
```json
"recipient_emails": [
    "theofficialjayesh@gmail.com",
    "jayeshjadhav1411@gmail.com"
]
```

### Add More Recipients:
Just add more email addresses to the array:
```json
"recipient_emails": [
    "email1@example.com",
    "email2@example.com", 
    "email3@example.com"
]
```

---

## 📊 **Monitoring & Logs**

### Check if Running:
```bash
ps aux | grep amul_email_monitor
```

### View Logs:
```bash
# Application logs
tail -f amul_monitor.log

# System output logs  
tail -f monitor_output.log

# Systemd logs (if using service)
journalctl -u amul-monitor -f
```

### Stop Monitor:
```bash
# Find process ID
ps aux | grep amul_email_monitor

# Kill process
kill <PROCESS_ID>

# Or if using systemd
sudo systemctl stop amul-monitor
```

---

## 🐛 **Troubleshooting**

### Common Issues:

**Chrome not found:**
```bash
# Ubuntu/Debian
sudo apt-get install google-chrome-stable

# CentOS/RHEL
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum install ./google-chrome-stable_current_x86_64.rpm
```

**Permission errors:**
```bash
chmod +x amul_email_monitor.py
chmod +x start_monitor.sh
```

**Email authentication:**
- Ensure Gmail App Password is correct
- Check firewall allows SMTP (port 587)

---

## 📧 **Current Configuration Status**

✅ **Products Monitored:**
- Amul Kool Protein Milkshake | Vanilla, 180 mL | Pack of 30
- Amul High Protein Rose Lassi, 200 mL | Pack of 30  
- Amul High Protein Blueberry Shake, 200 mL | Pack of 30

✅ **Email Recipients:**
- theofficialjayesh@gmail.com
- jayeshjadhav1411@gmail.com

✅ **Current Status:**
- Koolshake: **IN STOCK** ✅
- Rose Lassi: **OUT OF STOCK** ❌  
- Blueberry Shake: **OUT OF STOCK** ❌

---

## 🎉 **You're Ready!**

Your Amul Stock Monitor is now production-ready for 24/7 server deployment. The system will:

1. 🔄 **Monitor every 10 minutes**
2. 📧 **Send alerts to all recipients** when products come in stock
3. 📝 **Log all activities** for debugging
4. 🛡️ **Recover from errors** automatically
5. 🚀 **Run headlessly** without GUI requirements

Deploy it on your server and enjoy automated stock monitoring! 🎯
