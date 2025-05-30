from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from fastapi import Query
import json
from agents.classifier import detect_format_and_intent
from agents.email_agent import process_email
from agents.json_agent import validate_json
from agents.pdf_agent import process_pdf
from router.action_router import route_action
from utils.memory import log_to_memory, fetch_logs_by_agent, fetch_all_logs
from fastapi import APIRouter, Request

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



def extract_text_from_file(file_path: str, format_type: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")


def get_action_key(action_str: str) -> str:
    if action_str.startswith("alert"):
        return "risk_alert"
    elif "crm" in action_str:
        return "crm"
    elif action_str == "log_and_close":
        return "log_and_close"
    else:
        return "unknown"

@app.post("/risk_alert")
async def handle_risk_alert(request: Request):
    data = await request.json()

    return {"status": "received"}

@app.get("/logs/")
def get_logs(agent: str = Query(None, description="Filter logs by agent name")):
    if agent:
        logs = fetch_logs_by_agent(agent)
    else:
        logs = fetch_all_logs()
    result = [
        {"id": log[0], "timestamp": log[1], "agent": log[2], "data": json.loads(log[3])}
        for log in logs
    ]
    return JSONResponse(content=result)



@app.get("/")
def root():
    return {"message": "Multi-Agent System API is running"}


@app.post("/process/")
async def process_input(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    raw_text = ""
    if file.filename.endswith(".txt") or file.filename.endswith(".json"):
        raw_text = extract_text_from_file(
            file_path, "Email" if file.filename.endswith(".txt") else "JSON"
        )

    # Step 2: Classify format and intent
    try:
        format_type, intent = detect_format_and_intent(file_path, raw_text)
    except Exception as e:
        log_to_memory("api_error", {"error": f"Classification failed: {str(e)}", "file": file.filename})
        raise HTTPException(status_code=500, detail="Classification error")

    # Step 3: Route to appropriate agent
    try:
        if format_type == "Email":
            action = process_email(raw_text)
        elif format_type == "JSON":
            content = extract_text_from_file(file_path, "JSON")
            action = validate_json(content)
        elif format_type == "PDF":
            action = process_pdf(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
    except Exception as e:
        log_to_memory("api_error", {"error": f"Agent processing failed: {str(e)}", "file": file.filename})
        raise HTTPException(status_code=500, detail="Agent processing error")

    # Step 4: Trigger action routing
    payload = {
        "file": file.filename,
        "format": format_type,
        "intent": intent,
        "action": action,
    }

    action_key = get_action_key(action)

    try:
        route_action(action_key, payload)
    except Exception as e:
        log_to_memory("api_error", {
            "error": f"Routing failed: {str(e)}",
            "action": action,
            "file": file.filename
        })

    # Step 5: Log and respond
    log_to_memory("api", {"filename": file.filename, "format": format_type, "intent": intent, "action": action})

    return JSONResponse({
        "filename": file.filename,
        "format": format_type,
        "intent": intent,
        "agent_action": action,
        "message": "Processed successfully",
    })
