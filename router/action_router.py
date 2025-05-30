import requests
from utils.memory import log_to_memory
import time

def route_action(action: str, payload: dict = {}, retries: int = 3, return_response=False):
    endpoint_map = {
        "crm": "http://localhost:8000/crm",
        "risk_alert": "http://localhost:8000/risk_alert"
    }

    matched_endpoint = None
    for key, url in endpoint_map.items():
        if key in action:
            matched_endpoint = url
            break

    if not matched_endpoint:
        log_to_memory("action_router", {"error": f"No valid endpoint for action: {action}"})
        return "invalid_action"

    attempt = 0
    while attempt < retries:
        try:
            response = requests.post(matched_endpoint, json=payload, timeout=5)
            response.raise_for_status()
            log_to_memory("action_router", {"action": action, "payload": payload, "status": "success", "attempt": attempt + 1})
            if return_response:
                return response.json()
            return "success"
        except requests.RequestException as e:
            attempt += 1
            log_to_memory("action_router", {"action": action, "attempt": attempt, "error": str(e)})
            time.sleep(2 ** attempt)  # exponential backoff

    log_to_memory("action_router", {"action": action, "payload": payload, "status": "failed"})
    return "failed"
