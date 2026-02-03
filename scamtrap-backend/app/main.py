from fastapi import FastAPI, Header, HTTPException
from datetime import datetime

from app.schemas import ScamRequest, ScamResponse
from app.orchestrator import run_agents
from dotenv import load_dotenv
import os

load_dotenv()

print("Gemini key loaded:", bool(os.getenv("GEMINI_API_KEY")))

API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Agentic HoneyPot API")


@app.post("/handover", response_model=ScamResponse)
def handover(
    request: ScamRequest,
    x_api_key: str = Header(None)
):
    if  x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # ✅ Single source of truth
    result = run_agents(
        session_id=request.sessionId,
        message=request.message.text,
        conversation_history=request.conversationHistory
    )

    return {
        "status": "success",
        "sessionId": request.sessionId,

        # 🔑 DO NOT recompute this
        "scamDetected": result.get("scamDetected",False),

        "agentReply": {
            "sender": "user",
            "text": result.get("reply", ""),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },

        "engagementMetrics": {
            "totalMessagesExchanged": result["engagementMetrics"]["totalMessagesExchanged"]
        },


        "extractedIntelligence": result.get("extractedIntelligence", {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }),

        "agentNotes": (
            "Urgency and sensitive information request detected"
            if result["scamDetected"]
            else "No scam intent detected"
        )
    }