import json
from pydantic import BaseModel, ValidationError
from utils.memory import log_to_memory

class WebhookSchema(BaseModel):
    id: int
    type: str
    payload: dict

def validate_json(content: str) -> str:
    try:
        data = json.loads(content)
        WebhookSchema(**data)
        log_to_memory("json_agent", {"status": "valid", "data": data})
        return "valid"
    except ValidationError as e:
        error_details = e.errors()
        error_message = f"Validation error: {error_details}"
        log_to_memory("json_agent", {"status": "alert", "error": error_message, "raw_content": content})
        return f"alert: {error_message}"
    except json.JSONDecodeError as je:
        error_message = f"Invalid JSON: {str(je)}"
        log_to_memory("json_agent", {"status": "alert", "error": error_message, "raw_content": content})
        return f"alert: {error_message}"
