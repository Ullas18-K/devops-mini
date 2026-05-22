import os
import re
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timezone

app = Flask(__name__)

GEMINI_API_KEY      = os.environ.get("GEMINI_API_KEY", "")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"

COLOR_SUCCESS = 0x00FFA3
COLOR_FAILURE = 0xFF4D6D


def ask_gemini(error_log, build_url, job_name):
    prompt = f"""You are a senior DevOps engineer analyzing a Jenkins CI/CD build failure.
Job name : {job_name}
Build URL : {build_url}
---- ERROR LOG ----
{error_log[-4000:]}
-------------------
Respond ONLY with valid JSON (no markdown, no backticks):
{{"summary": "One-line plain-English root cause", "fix": "2-4 sentence concrete fix"}}"""
    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )
        resp.raise_for_status()
        raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        return json.loads(raw)
    except Exception as exc:
        return {"summary": "Could not parse Gemini response.", "fix": f"Manual investigation required. Error: {exc}"}


def send_discord_embed(status, job_name, build_number, build_url, error_log, summary, fix):
    is_success = status.lower() == "success"
    color = COLOR_SUCCESS if is_success else COLOR_FAILURE
    status_icon = "SUCCESS" if is_success else "FAILED"
    timestamp = datetime.now(timezone.utc).isoformat()
    log_snippet = error_log[-800:].strip() if error_log else "No log provided."

    fields = [
        {"name": "Build URL",      "value": f"[Open in Jenkins]({build_url})", "inline": False},
        {"name": "Error Summary",  "value": summary or "No summary available.", "inline": False},
        {"name": "Suggested Fix",  "value": fix or "No suggestion available.", "inline": False},
    ]
    if not is_success and log_snippet:
        fields.append({"name": "Log Snippet", "value": f"```\n{log_snippet[:900]}\n```", "inline": False})

    embed = {
        "title": f"[{status_icon}] {job_name} - Build #{build_number}",
        "description": "Build completed successfully!" if is_success else "Build failed. Gemini has analyzed the error below.",
        "color": color,
        "fields": fields,
        "footer": {"text": "NeuralDock - Jenkins CI/CD Bot"},
        "timestamp": timestamp,
    }
    payload = {"username": "NeuralDock Bot", "embeds": [embed]}

    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as exc:
        print(f"[Discord] Failed: {exc}")
        return False


@app.route("/jenkins-webhook", methods=["POST"])
def jenkins_webhook():
    data = request.get_json(silent=True) or {}
    job_name     = data.get("job_name", "Unknown Job")
    build_number = data.get("build_number", "?")
    build_url    = data.get("build_url", "#")
    status       = data.get("status", "UNKNOWN")
    error_log = data.get("error_log") or data.get("log", "")

    print(f"[Webhook] {job_name} #{build_number} -> {status}")

    if status.upper() == "FAILURE" and error_log:
        analysis = ask_gemini(error_log, build_url, job_name)
    else:
        analysis = {"summary": "Build completed without errors.", "fix": "No action needed."}

    sent = send_discord_embed(status, job_name, build_number, build_url, error_log, analysis["summary"], analysis["fix"])

    if sent:
        return jsonify({"ok": True, "message": "Discord embed sent."}), 200
    else:
        return jsonify({"ok": False, "message": "Discord send failed."}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running", "service": "NeuralDock Discord Bot"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=False)
