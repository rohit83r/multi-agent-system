import os
import mimetypes
import requests
from dotenv import load_dotenv
from utils.memory import log_to_memory

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def detect_format_and_intent(file_path: str, text_content: str) -> tuple[str, str]:
    # Detect file format robustly
    format_guess, _ = mimetypes.guess_type(file_path)
    if format_guess:
        if "pdf" in format_guess:
            format_type = "PDF"
        elif "json" in format_guess:
            format_type = "JSON"
        elif "plain" in format_guess or "html" in format_guess:
            format_type = "Email"
        else:
            format_type = "Unknown"
    else:
        ext = file_path.lower()
        if ext.endswith(".pdf"):
            format_type = "PDF"
        elif ext.endswith(".json"):
            format_type = "JSON"
        elif ext.endswith(".eml") or ext.endswith(".msg") or ext.endswith(".txt"):
            format_type = "Email"
        else:
            format_type = "Unknown"

    prompt = f"""
You are an expert in understanding document context.
Classify the following content into one of these business intents:
- RFQ (Request for Quotation)
- Complaint
- Invoice
- Regulation
- Fraud Risk

Content:
{text_content}

Only return the intent label (one of RFQ, Complaint, Invoice, Regulation, Fraud Risk).
"""

    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is missing! Please set GEMINI_API_KEY in your environment or .env file.")

    try:
        response = requests.post(
            GEMINI_API_URL,
            params={"key": GEMINI_API_KEY},
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            },
        )
        response.raise_for_status()
        res_json = response.json()
        intent = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        if not intent:
            intent = "Unknown"
    except Exception as e:
        intent = "Unknown"
        print(f"Error calling Gemini API: {e}")

    log_to_memory("classifier", {"format": format_type, "intent": intent})
    return format_type, intent
