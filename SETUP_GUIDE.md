# 🚀 NeuralDock Setup Guide

## Prerequisites

- Docker Desktop installed and running
- Git installed
- Python 3.10+ (optional, for local testing)
- Discord account (for notifications)
- Google account (for Gemini API)

---

## 📋 Step-by-Step Setup

### **1. Get Your API Keys**

#### **A. Gemini API Key (FREE)**
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

#### **B. Discord Webhook URL**
1. Open Discord and go to your server
2. Right-click on a channel → **Edit Channel**
3. Go to **Integrations** → **Webhooks**
4. Click **New Webhook**
5. Give it a name (e.g., "NeuralDock Bot")
6. Copy the **Webhook URL** (looks like: `https://discord.com/api/webhooks/...`)

---

### **2. Configure Environment Variables**

Edit the `.env` file in the project root:

```bash
GEMINI_API_KEY=AIzaSyC...your_actual_key_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdef...
```

⚠️ **Important:** Never commit `.env` to Git! It's already in `.gitignore`.

---

### **3. Run the Application**

#### **Option A: Using Docker Compose (Recommended)**

```bash
# Build and start both services
docker-compose up -d --build

# Check if containers are running
docker ps

# View logs
docker logs -f neuraldock-app
docker logs -f neuraldock-bot
```

#### **Option B: Run Individually**

```bash
# Build main app
docker build -t neuraldock-app .
docker run -d -p 5000:5000 --env-file .env --name neuraldock-app neuraldock-app

# Build bot
docker build -t neuraldock-bot ./discord_bot
docker run -d -p 6000:6000 --env-file .env --name neuraldock-bot neuraldock-bot
```

---

### **4. Test the Application**

#### **Test Main App:**
1. Open browser: http://localhost:5000
2. Type a prompt: "Explain Docker in one sentence"
3. Click **Generate**
4. You should see a response from Gemini!

#### **Test Bot Health:**
```bash
curl http://localhost:6000/health
```

Expected response:
```json
{"status": "running", "service": "NeuralDock Discord Bot"}
```

---

## 🧪 Simulate Jenkins Failure (Test Discord Bot)

### **Method 1: Using the Test Script (Easiest)**

```bash
# Make sure bot is running
docker ps | grep neuraldock-bot

# Run the test script
python discord_bot/test_webhook.py
```

This will:
- Send a fake Jenkins failure to the bot
- Bot analyzes the error with Gemini
- Posts a rich embed to your Discord channel

---

### **Method 2: Manual cURL Test**

```bash
curl -X POST http://localhost:6000/jenkins-webhook \
  -H "Content-Type: application/json" \
  -d "{
    \"job_name\": \"test-pipeline\",
    \"build_number\": \"42\",
    \"build_url\": \"http://localhost:8080/job/test/42\",
    \"status\": \"FAILURE\",
    \"error_log\": \"ERROR: pip install failed - package not found\"
  }"
```

---

### **Method 3: Trigger Real Jenkins Failure**

If you have Jenkins set up:

1. **Intentionally break the build:**
   - Edit `requirements.txt` and add a typo:
     ```
     flask
     requestsssss  ← typo here
     ```
   - Commit and push

2. **Jenkins will:**
   - Try to build
   - Fail at `pip install`
   - Send error to bot webhook
   - Bot analyzes with Gemini
   - Posts to Discord

3. **Fix it:**
   - Correct the typo
   - Commit and push
   - Jenkins succeeds
   - Bot posts success message

---

## 🔍 Troubleshooting

### **App not responding?**
```bash
# Check logs
docker logs neuraldock-app

# Restart
docker restart neuraldock-app
```

### **Bot not posting to Discord?**
```bash
# Check bot logs
docker logs neuraldock-bot

# Verify webhook URL is correct
docker exec neuraldock-bot env | grep DISCORD_WEBHOOK_URL

# Test webhook manually
curl -X POST "YOUR_DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message from NeuralDock!"}'
```

### **Gemini API errors?**
```bash
# Check if API key is set
docker exec neuraldock-app env | grep GEMINI_API_KEY

# Verify key is valid at: https://aistudio.google.com/app/apikey
```

### **Port already in use?**
```bash
# Find what's using the port
netstat -ano | findstr :5000
netstat -ano | findstr :6000

# Stop the process or change ports in docker-compose.yml
```

---

## 🛑 Stop Everything

```bash
# Stop and remove containers
docker-compose down

# Remove images (optional)
docker rmi neuraldock-llm:latest
docker rmi neuraldock-bot:latest
```

---

## 📊 Expected Discord Embed (Failure)

When a build fails, you'll see:

```
🔴 [FAILED] test-pipeline - Build #42

Build completed. Gemini has analyzed the error below.

Build URL: [Open in Jenkins](http://localhost:8080/...)

Error Summary:
Package 'requestsssss' not found in PyPI repository

Suggested Fix:
Check requirements.txt for typos. The correct package name is 'requests' 
(without extra 's'). Update the file and rebuild.

Log Snippet:
```
ERROR: Could not find a version that satisfies the requirement requestsssss
ERROR: No matching distribution found for requestsssss
```
```

---

## 🎯 Quick Commands Reference

```bash
# Start everything
docker-compose up -d --build

# View logs (live)
docker logs -f neuraldock-app
docker logs -f neuraldock-bot

# Check status
docker ps

# Test bot
python discord_bot/test_webhook.py

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

---

## 🚀 Next Steps

1. ✅ Set up Jenkins pipeline (see README.md)
2. ✅ Configure Jenkins credentials
3. ✅ Test full CI/CD flow
4. ✅ Customize Discord embed colors/messages
5. ✅ Add more AI analysis features

---

## 💡 Pro Tips

- **Free Tier Limits:** Gemini API has generous free limits (60 requests/minute)
- **Discord Rate Limits:** Don't spam webhooks (30 messages/minute max)
- **Logs:** Always check logs first when debugging
- **Environment:** Use different `.env` files for dev/prod
- **Security:** Never expose your API keys publicly

---

Need help? Check the logs or open an issue! 🎉
