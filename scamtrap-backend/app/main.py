from fastapi import FastAPI, Header, HTTPException
from datetime import datetime

from app.schemas import ScamRequest, ScamResponse
from app.orchestrator import run_agents

API_KEY = "YOUR_SECRET_API_KEY"  # optional for now

app = FastAPI(title="Agentic HoneyPot API")


@app.post("/handover", response_model=ScamResponse)
def handover(
    request: ScamRequest,
    x_api_key: str = Header(None)
):
    # 🔐 Optional API-key check (GUVI compliant)
    if x_api_key is not None and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 🔁 Run agent pipeline
    result = run_agents(
        session_id=request.sessionId,
        message=request.message.text,
        conversation_history=request.conversationHistory
    )

    classification = result.get("classification",{})
    keywords = result.get("extractedIntelligence", {}).get("suspiciousKeywords", [])

    scam_detected = (
        classification.get("is_scam", False)
        or "otp" in keywords
        or "account will be blocked" in request.message.text.lower()
    )


    agent_notes = (
        "Urgency and sensitive information request detected"
        if scam_detected
        else "No scam intent detected"
    )

    return {
        "status": "success",
        "sessionId": request.sessionId,
        "scamDetected": scam_detected,

        # 🧠 THIS WAS MISSING BEFORE
        "agentReply": {
            "sender": "user",
            "text": result.get("reply",""),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },

        "engagementMetrics": {
            "totalMessagesExchanged": len(request.conversationHistory) + 1
        },

        "extractedIntelligence": result.get("extractedIntelligence", {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }),
        "agentNotes": agent_notes
    }
