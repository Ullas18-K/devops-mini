# 🎯 NeuralDock Quick Reference

## 🚀 Getting Started (3 Steps)

### **Step 1: Get API Keys**
```
Gemini API:  https://aistudio.google.com/app/apikey
Discord:     Server → Channel → Integrations → Webhooks → New Webhook
```

### **Step 2: Configure .env**
```bash
GEMINI_API_KEY=AIzaSyC...your_key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### **Step 3: Run**
```bash
# Double-click this file:
quick-start.bat

# Or manually:
docker-compose up -d --build
```

---

## 🧪 Test Discord Bot (3 Methods)

### **Method 1: Batch Script (Easiest)**
```bash
# Double-click:
test-discord-bot.bat
```

### **Method 2: Python Script**
```bash
python discord_bot\test_webhook.py
```

### **Method 3: cURL**
```bash
curl -X POST http://localhost:6000/jenkins-webhook ^
  -H "Content-Type: application/json" ^
  -d "{\"job_name\":\"test\",\"build_number\":\"1\",\"build_url\":\"http://test\",\"status\":\"FAILURE\",\"error_log\":\"ERROR: Build failed\"}"
```

---

## 📋 Common Commands

| Action | Command |
|--------|---------|
| **Start everything** | `docker-compose up -d --build` |
| **Stop everything** | `docker-compose down` |
| **View app logs** | `docker logs -f neuraldock-app` |
| **View bot logs** | `docker logs -f neuraldock-bot` |
| **Check status** | `docker ps` |
| **Restart app** | `docker restart neuraldock-app` |
| **Restart bot** | `docker restart neuraldock-bot` |
| **Test bot** | `test-discord-bot.bat` |
| **Check setup** | `check-setup.bat` |

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:5000 | Web UI for Gemini LLM |
| **Bot Health** | http://localhost:6000/health | Bot status check |
| **Bot Webhook** | http://localhost:6000/jenkins-webhook | Jenkins notifications |

---

## 🔧 Troubleshooting

### **App not loading?**
```bash
docker logs neuraldock-app
docker restart neuraldock-app
```

### **Bot not posting to Discord?**
```bash
# Check logs
docker logs neuraldock-bot

# Test webhook directly
curl -X POST "YOUR_DISCORD_WEBHOOK_URL" ^
  -H "Content-Type: application/json" ^
  -d "{\"content\":\"Test from NeuralDock\"}"
```

### **Port already in use?**
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process or change port in docker-compose.yml
```

### **Gemini API errors?**
- Check if key is valid: https://aistudio.google.com/app/apikey
- Verify `.env` file has correct key
- Check rate limits (60 requests/minute on free tier)

---

## 🎨 Simulate Different Scenarios

### **Success Build**
```bash
curl -X POST http://localhost:6000/jenkins-webhook ^
  -H "Content-Type: application/json" ^
  -d "{\"job_name\":\"my-pipeline\",\"build_number\":\"10\",\"build_url\":\"http://jenkins/job/10\",\"status\":\"SUCCESS\",\"error_log\":\"\"}"
```

### **Docker Build Failure**
```bash
curl -X POST http://localhost:6000/jenkins-webhook ^
  -H "Content-Type: application/json" ^
  -d "{\"job_name\":\"docker-build\",\"build_number\":\"5\",\"build_url\":\"http://jenkins/job/5\",\"status\":\"FAILURE\",\"error_log\":\"ERROR: docker build failed\\nStep 3/8 : RUN pip install -r requirements.txt\\nERROR: Could not find a version that satisfies the requirement flaskkkk\"}"
```

### **Python Syntax Error**
```bash
curl -X POST http://localhost:6000/jenkins-webhook ^
  -H "Content-Type: application/json" ^
  -d "{\"job_name\":\"syntax-check\",\"build_number\":\"3\",\"build_url\":\"http://jenkins/job/3\",\"status\":\"FAILURE\",\"error_log\":\"SyntaxError: invalid syntax\\nFile app.py, line 42\\n  if x = 5:\\n       ^\\nSyntaxError: invalid syntax\"}"
```

---

## 📊 What to Expect

### **Discord Embed (Failure)**
```
🔴 [FAILED] docker-build - Build #5

Build failed. Gemini has analyzed the error below.

📎 Build URL: [Open in Jenkins](http://jenkins/job/5)

❌ Error Summary:
Package name typo in requirements.txt - 'flaskkkk' should be 'flask'

💡 Suggested Fix:
Open requirements.txt and correct the package name from 'flaskkkk' 
to 'flask'. Then rebuild the Docker image.

📝 Log Snippet:
```
ERROR: Could not find a version that satisfies the requirement flaskkkk
ERROR: No matching distribution found for flaskkkk
```
```

### **Discord Embed (Success)**
```
🟢 [SUCCESS] docker-build - Build #11

Build completed successfully!

📎 Build URL: [Open in Jenkins](http://jenkins/job/11)

✅ Error Summary:
Build completed without errors.

💡 Suggested Fix:
No action needed.
```

---

## 🎯 Project Structure

```
neuraldock-ai-devops/
├── app.py                    ← Main Flask app
├── templates/index.html      ← Beautiful UI
├── discord_bot/
│   ├── bot.py               ← Discord webhook + AI analysis
│   └── test_webhook.py      ← Test script
├── .env                      ← Your API keys (DO NOT COMMIT!)
├── docker-compose.yml        ← Orchestrates both services
├── Jenkinsfile              ← CI/CD pipeline
├── quick-start.bat          ← Easy startup script
├── test-discord-bot.bat     ← Test bot easily
├── check-setup.bat          ← Verify configuration
└── SETUP_GUIDE.md           ← Detailed instructions
```

---

## 💡 Pro Tips

1. **Always check logs first** when debugging
2. **Use `check-setup.bat`** to verify everything is configured
3. **Test bot locally** before setting up Jenkins
4. **Free tier limits:** Gemini (60 req/min), Discord (30 msg/min)
5. **Never commit `.env`** - it's in `.gitignore` for a reason
6. **Restart containers** after changing `.env` file

---

## 🎉 Success Checklist

- [ ] Docker Desktop installed and running
- [ ] `.env` file created with valid API keys
- [ ] Containers running: `docker ps`
- [ ] Main app accessible: http://localhost:5000
- [ ] Bot health check: http://localhost:6000/health
- [ ] Discord bot test successful
- [ ] Received Discord notification

---

**Need more help?** See `SETUP_GUIDE.md` for detailed instructions!
