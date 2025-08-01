import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/v1/inference", methods=["POST"])
def infer():
    data = request.get_json()
    prompt = data.get("prompt", "Say hello to SAP GenAI!")

    # Use SAP Generative AI Hub endpoint
    genai_url = "https://genaihub-aicore.cfapps.eu10.hana.ondemand.com/inference/palm/chat/completion"

    headers = {
        "Authorization": f"Bearer {os.environ.get('GENAI_TOKEN')}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(genai_url, headers=headers, json=payload)
    response.raise_for_status()

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
