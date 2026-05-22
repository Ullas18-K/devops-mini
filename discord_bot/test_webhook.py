#!/usr/bin/env python3
"""
Simulates a Jenkins failure POST to the bot.
Run this to test Discord notifications without Jenkins.

Usage:
    python3 test_webhook.py
"""
import requests, json

BOT_URL = "http://localhost:6000/jenkins-webhook"

FAKE_ERROR_LOG = """
+ docker build -t neuraldock-llm:latest .
Step 5/8 : RUN pip install --no-cache-dir -r requirements.txt
ERROR: Could not find a version that satisfies the requirement flaskk==2.3.0
ERROR: No matching distribution found for flaskk==2.3.0
The command returned a non-zero code: 1
"""

payload = {
    "job_name"     : "neuraldock-pipeline",
    "build_number" : "7",
    "build_url"    : "http://localhost:8080/job/neuraldock-pipeline/7/",
    "status"       : "FAILURE",
    "error_log"    : FAKE_ERROR_LOG,
}

print("Sending test webhook to", BOT_URL)
print("-" * 50)
try:
    r = requests.post(BOT_URL, json=payload, timeout=60)
    print(f"HTTP {r.status_code}")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
