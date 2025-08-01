import requests
import os

def run_genai_prompt():
    endpoint = os.environ.get("GENAI_ENDPOINT")  # Set in execution config
    apikey = os.environ.get("GENAI_APIKEY")      # Set in execution config

    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What is sustainability in business?"}
        ]
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    print("Response:\n", response.text)

if __name__ == "__main__":
    run_genai_prompt()
