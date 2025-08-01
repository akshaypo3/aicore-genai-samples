import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Dummy example of using SAP Generative AI Hub (replace URL/token later)
SAP_GENAI_API_URL = "https://generativeai.cfapps.eu10.hana.ondemand.com/inference/v1/completions"
SAP_GENAI_TOKEN = "<your-token-here>"  # We'll show how to get this securely

@app.route("/v1/predict", methods=["POST"])
def predict():
    data = request.get_json()
    prompt = data.get("prompt", "")

    headers = {
        "Authorization": f"Bearer {SAP_GENAI_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": {
            "name": "gemini-1.5-flash"
        },
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(SAP_GENAI_API_URL, headers=headers, json=payload)
    result = response.json()

    # Just extract response text (depends on structure)
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    return jsonify({"response": content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
