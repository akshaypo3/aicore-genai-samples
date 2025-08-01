# main.py — minimal working handler
import json

def handle(request):
    # This function will be called by SAP AI Core
    body = request.get_json()
    prompt = body.get("prompt", "Say something")

    response = {
        "response": f"Echoing back your prompt: {prompt}"
    }

    return (json.dumps(response), 200, {"Content-Type": "application/json"})
