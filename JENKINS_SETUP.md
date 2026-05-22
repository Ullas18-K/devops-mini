# 🔧 Jenkins Setup & Real Error Testing

## ✅ What I Just Fixed

**BEFORE:** Jenkinsfile was sending generic message: `"Build failed. Check Jenkins console output for details."`

**NOW:** Jenkinsfile captures the **actual last 200 lines of build log** and sends them to your Discord bot for AI analysis!

---

## 🚀 Jenkins Setup Steps

### **1. Install Jenkins**

#### **Option A: Docker (Recommended)**
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

#### **Option B: Windows Installer**
Download from: https://www.jenkins.io/download/

---

### **2. Initial Jenkins Configuration**

1. **Get initial admin password:**
   ```bash
   # If using Docker:
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   
   # If installed on Windows:
   # Check: C:\Program Files\Jenkins\secrets\initialAdminPassword
   ```

2. **Open Jenkins:** http://localhost:8080

3. **Install suggested plugins**

4. **Create admin user**

---

### **3. Configure Jenkins Credentials**

1. Go to: **Manage Jenkins** → **Credentials** → **System** → **Global credentials**

2. **Add GEMINI_API_KEY:**
   - Click **Add Credentials**
   - Kind: **Secret text**
   - Secret: `AIzaSyC...your_actual_gemini_key`
   - ID: `GEMINI_API_KEY`
   - Description: `Gemini API Key for LLM`
   - Click **Create**

3. **Add DISCORD_WEBHOOK_URL (Optional - if you want it in Jenkins):**
   - Click **Add Credentials**
   - Kind: **Secret text**
   - Secret: `https://discord.com/api/webhooks/...`
   - ID: `DISCORD_WEBHOOK_URL`
   - Description: `Discord Webhook for notifications`
   - Click **Create**

---

### **4. Create Pipeline Job**

1. **New Item** → Enter name: `neuraldock-pipeline` → **Pipeline** → OK

2. **Pipeline Configuration:**
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/your-username/neuraldock-ai-devops.git`
   - Branch: `*/main` (or `*/master`)
   - Script Path: `Jenkinsfile`

3. **Save**

---

### **5. Important: Network Configuration**

The Jenkinsfile uses: `http://host.docker.internal:6000/jenkins-webhook`

This works when:
- ✅ Jenkins is running in Docker (on Windows/Mac)
- ✅ Bot is running on host machine

**If both Jenkins and Bot are in Docker:**
```groovy
// Change this line in Jenkinsfile:
BOT_WEBHOOK = "http://neuraldock-bot:6000/jenkins-webhook"

// And add to docker-compose.yml:
networks:
  - jenkins-network
```

**If Jenkins is on Windows (not Docker):**
```groovy
// Change this line in Jenkinsfile:
BOT_WEBHOOK = "http://localhost:6000/jenkins-webhook"
```

---

## 🧪 Test Real Errors

### **Test 1: Python Package Typo**

1. **Break the build:**
   ```bash
   # Edit requirements.txt
   echo flask > requirements.txt
   echo requestsssss >> requirements.txt  # Typo!
   
   git add requirements.txt
   git commit -m "test: introduce package typo"
   git push
   ```

2. **Jenkins will:**
   - Clone repo
   - Try to build Docker image
   - **FAIL** at `pip install -r requirements.txt`
   - Capture error log:
     ```
     ERROR: Could not find a version that satisfies the requirement requestsssss
     ERROR: No matching distribution found for requestsssss
     The command '/bin/sh -c pip install --no-cache-dir -r requirements.txt' returned a non-zero code: 1
     ```
   - Send to bot webhook

3. **Bot will:**
   - Receive the error log
   - Send to Gemini for analysis
   - Gemini responds:
     ```json
     {
       "summary": "Package name typo in requirements.txt - 'requestsssss' should be 'requests'",
       "fix": "Open requirements.txt and correct line 2 from 'requestsssss' to 'requests'. Then rebuild."
     }
     ```
   - Post rich Discord embed with analysis

4. **Fix it:**
   ```bash
   echo flask > requirements.txt
   echo requests >> requirements.txt  # Fixed!
   
   git add requirements.txt
   git commit -m "fix: correct package name"
   git push
   ```

5. **Jenkins succeeds** → Bot posts success message

---

### **Test 2: Python Syntax Error**

1. **Break app.py:**
   ```python
   # Add this line somewhere in app.py:
   if x = 5:  # Wrong! Should be ==
       pass
   ```

2. **Jenkins will:**
   - Clone repo
   - Build Docker image (succeeds)
   - Run container
   - Container crashes immediately
   - Capture error:
     ```
     SyntaxError: invalid syntax
     File "/app/app.py", line 42
       if x = 5:
            ^
     SyntaxError: invalid syntax
     ```

3. **Gemini analyzes:**
   ```json
   {
     "summary": "Python syntax error - assignment operator '=' used instead of comparison '==' in if statement",
     "fix": "Change line 42 in app.py from 'if x = 5:' to 'if x == 5:' or remove the line if it's test code."
   }
   ```

---

### **Test 3: Missing Environment Variable**

1. **Remove GEMINI_API_KEY from Jenkinsfile:**
   ```groovy
   // Comment out this line:
   // GEMINI_API_KEY = credentials('GEMINI_API_KEY')
   ```

2. **Jenkins will:**
   - Build succeeds
   - Container starts
   - App runs but API calls fail
   - Health check might pass but app is broken

3. **Better approach - add validation:**
   ```python
   # Add to app.py at the top:
   if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
       raise ValueError("GEMINI_API_KEY environment variable not set!")
   ```

---

### **Test 4: Docker Build Context Error**

1. **Break Dockerfile:**
   ```dockerfile
   # Change this line:
   COPY requirements.txt .
   # To:
   COPY requirements-typo.txt .  # File doesn't exist!
   ```

2. **Jenkins will:**
   - Try to build Docker image
   - **FAIL** with:
     ```
     COPY failed: file not found in build context or excluded by .dockerignore: 
     stat requirements-typo.txt: file does not exist
     ```

3. **Gemini analyzes:**
   ```json
   {
     "summary": "Dockerfile references non-existent file 'requirements-typo.txt'",
     "fix": "Check Dockerfile line 4. The file should be 'requirements.txt' not 'requirements-typo.txt'. Correct the filename and rebuild."
   }
   ```

---

## 📊 What Gets Sent to Gemini

The bot receives this JSON from Jenkins:

```json
{
  "job_name": "neuraldock-pipeline",
  "build_number": "15",
  "build_url": "http://localhost:8080/job/neuraldock-pipeline/15/",
  "status": "FAILURE",
  "error_log": "Started by user admin\n[Pipeline] Start of Pipeline\n[Pipeline] node\n...\nERROR: Could not find a version that satisfies the requirement requestsssss\nERROR: No matching distribution found for requestsssss\nThe command '/bin/sh -c pip install --no-cache-dir -r requirements.txt' returned a non-zero code: 1\n[Pipeline] End of Pipeline\nFinished: FAILURE"
}
```

The bot then:
1. Extracts last 4000 chars of error_log (to fit Gemini's context)
2. Sends to Gemini with prompt asking for root cause + fix
3. Parses Gemini's JSON response
4. Creates Discord embed with the analysis

---

## 🎯 Expected Discord Output (Real Error)

```
🔴 [FAILED] neuraldock-pipeline - Build #15

Build failed. Gemini has analyzed the error below.

📎 Build URL: [Open in Jenkins](http://localhost:8080/job/neuraldock-pipeline/15/)

❌ Error Summary:
Package name typo in requirements.txt - 'requestsssss' should be 'requests'

💡 Suggested Fix:
Open requirements.txt and correct line 2 from 'requestsssss' to 'requests'. 
The package name has extra 's' characters. After fixing, commit and push to 
trigger a new build.

📝 Log Snippet:
ERROR: Could not find a version that satisfies the requirement requestsssss
ERROR: No matching distribution found for requestsssss
The command '/bin/sh -c pip install --no-cache-dir -r requirements.txt' 
returned a non-zero code: 1
```

---

## ✅ Verification Checklist

Before testing real errors:

- [ ] Jenkins is running and accessible
- [ ] Pipeline job created and configured
- [ ] GEMINI_API_KEY credential added to Jenkins
- [ ] Bot container is running: `docker ps | grep neuraldock-bot`
- [ ] Bot is accessible from Jenkins (check network config)
- [ ] Test webhook works: `test-discord-bot.bat`
- [ ] Git repository connected to Jenkins

---

## 🔧 Troubleshooting

### **Jenkins can't reach bot webhook**

```bash
# Test from Jenkins container:
docker exec jenkins curl -X POST http://host.docker.internal:6000/health

# If fails, check bot logs:
docker logs neuraldock-bot

# Verify bot is listening:
netstat -an | findstr :6000
```

### **Bot receives webhook but doesn't post to Discord**

```bash
# Check bot logs:
docker logs neuraldock-bot

# Test Discord webhook directly:
curl -X POST "YOUR_DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test from command line"}'
```

### **Gemini API errors**

```bash
# Check if bot has API key:
docker exec neuraldock-bot env | grep GEMINI_API_KEY

# Verify key is valid:
# Go to: https://aistudio.google.com/app/apikey
```

---

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ Jenkins build fails (red in Jenkins UI)
2. ✅ Jenkins console shows: `❌ Discord notified — build failed with actual error log.`
3. ✅ Bot logs show: `[Webhook] neuraldock-pipeline #15 -> FAILURE`
4. ✅ Discord channel receives embed with **actual error analysis**
5. ✅ Gemini's analysis makes sense and suggests correct fix

---

**Now your setup is production-ready!** 🚀

The bot will analyze **real errors** from Jenkins and provide **intelligent suggestions** powered by Gemini AI.
