import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        answer = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"response": answer})

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500
    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected response from Gemini API."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
