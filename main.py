# main.py
import json
import requests

def handle(req):
    body = json.loads(req)
    prompt = body.get("prompt", "Say hello")

    response = requests.post(
        "https://generative-ai.cfapps.eu10.hana.ondemand.com/inference/pipeline/gpt-4",  # change to correct model ID
        headers={
            "Authorization": f"Bearer {get_token()}",
            "Content-Type": "application/json"
        },
        json={
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return {"response": response.json()}

def get_token():
    # Get token using service binding (SAP Launchpad provides it)
    with open('/etc/secrets/sap-iam/service-key.json') as f:
        key = json.load(f)

    auth_url = key["url"] + "/oauth/token"
    client_id = key["clientid"]
    client_secret = key["clientsecret"]

    res = requests.post(
        auth_url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret)
    )
    return res.json()["access_token"]
