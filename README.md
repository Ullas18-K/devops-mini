# NeuralDock — Serverless LLM DevOps Demo

```
Architecture:  User → HTML UI → Flask API → Gemini 2.0 LLM
DevOps Stack:  Git → Jenkins → Docker → localhost:5000
Discord Bot:   Jenkins failure → Gemini analysis → Discord embed
```

## Project Structure

```
serverless-llm-devops/
├── app.py                  ← Flask web app
├── requirements.txt        ← flask, requests
├── templates/
│   └── index.html          ← Stylish frontend UI
├── Dockerfile              ← Builds neuraldock-app (port 5000)
├── docker-compose.yml      ← Runs both services together
├── Jenkinsfile             ← 4-stage CI/CD pipeline + Discord notify
├── .env.example            ← Copy to .env and fill in keys
├── .gitignore
└── discord_bot/
    ├── bot.py              ← Webhook server + Gemini + Discord embed
    ├── requirements.txt
    ├── Dockerfile          ← Builds neuraldock-bot (port 6000)
    └── test_webhook.py     ← Test bot without Jenkins
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/<your-username>/serverless-llm-devops.git
cd serverless-llm-devops

# 2. Set up environment variables
cp .env.example .env
# Edit .env and fill in GEMINI_API_KEY and DISCORD_WEBHOOK_URL

# 3. Run both services
docker-compose up -d --build

# 4. Open the app
# http://localhost:5000
```

## Demo Commands

```bash
docker ps                          # show running containers
docker images                      # show built images
docker logs -f neuraldock-app      # live app logs
docker logs -f neuraldock-bot      # live bot logs
docker-compose down                # stop everything
```

## Jenkins Setup

1. Add credentials (Manage Jenkins → Credentials):
   - ID: `GEMINI_API_KEY` (Secret text)
   - ID: `DISCORD_WEBHOOK_URL` (Secret text)

2. New Pipeline job → Pipeline script from SCM → Git → your repo URL

3. Build Now — watch 4 stages run, Discord embed appears automatically

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Serves HTML frontend |
| POST | `/generate` | Sends prompt to Gemini, returns response |
| POST | `/jenkins-webhook` | Receives Jenkins build result (bot, port 6000) |
| GET | `/health` | Health check (bot, port 6000) |

## Get API Keys

- **Gemini**: https://aistudio.google.com/app/apikey (free)
- **Discord Webhook**: Server → Channel Settings → Integrations → Webhooks → New Webhook
