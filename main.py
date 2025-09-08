from fastapi import FastAPI, UploadFile, File, Query
from services.file_parser import parse_file
from services.llm_transformer import call_llm_with_retry
from config.settings import settings
from pathlib import Path
import json
import httpx

app = FastAPI()
OLLAMA_URL = f"{settings.OLLAMA_HOST}/api/chat"

APP_SCHEMA_PATH = Path("schemas/BusinessApplication.json")
with APP_SCHEMA_PATH.open("r") as f:
    business_app_schema = json.load(f)

APP_TYPE_SCHEMA_PATH = Path("schemas/DisconnectedApplicationType.json")
with APP_TYPE_SCHEMA_PATH.open("r") as f:
    app_type_schema = json.load(f)

@app.post("/onboard")
async def onboard_app(file: UploadFile = File(...), entityType: str = Query(...)):
    rows_to_send = await parse_file(file, entityType)
    llm_responses = []

    async with httpx.AsyncClient(timeout=60) as client:
        for row in rows_to_send:
            user_message = json.dumps(row)
            payload = {
                "model": settings.MODEL_NAME,
                "temperature": 0,
                "messages": [{"role": "user", "content": user_message}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "create_app_config" if entityType == "Business Application" else "create_app_type_config",
                            "description": "Generate IAP App Onboarding Configuration JSON",
                            "parameters": business_app_schema if entityType == "Business Application" else app_type_schema,
                            "required": True
                        }
                    }
                ],
                "stream": False
            }
            arguments = await call_llm_with_retry(client, OLLAMA_URL, payload,
                                                   business_app_schema if entityType == "Business Application" else app_type_schema)
            llm_responses.append(arguments)
    return llm_responses
