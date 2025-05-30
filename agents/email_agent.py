import os
import requests
from utils.memory import log_to_memory
from textblob import TextBlob

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

POLARITY_ANGRY_THRESHOLD = -0.3
POLARITY_NEUTRAL_THRESHOLD = 0.2

def call_gemini_api(prompt: str) -> str:
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
                            {"text": prompt.strip()}
                        ]
                    }
                ]
            },
        )
        response.raise_for_status()
        res_json = response.json()
        intent = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        return intent
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "neutral"  # fallback tone

def process_email(content: str) -> str:
    blob = TextBlob(content)
    polarity = blob.sentiment.polarity

    if polarity < POLARITY_ANGRY_THRESHOLD:
        tone = "angry"
    elif abs(polarity) < POLARITY_NEUTRAL_THRESHOLD:
        # uncertain tone, ask Gemini LLM
        prompt = f"""
Analyze the tone of the following email:
---
{content}
---
Is the tone: angry, polite, neutral, or threatening?
"""
        llm_tone = call_gemini_api(prompt).lower()
        if llm_tone in ["angry", "threatening"]:
            tone = "angry"
        elif llm_tone == "polite":
            tone = "polite"
        else:
            tone = "neutral"
    else:
        tone = "polite"

    urgency_keywords = ["urgent", "asap", "immediately", "now"]
    urgency = "high" if any(word in content.lower() for word in urgency_keywords) else "routine"

    if tone == "angry" and urgency == "high":
        action = "POST /crm/escalate"
    else:
        action = "log_and_close"

    log_to_memory("email_agent", {"tone": tone, "urgency": urgency, "action": action})
    return action
