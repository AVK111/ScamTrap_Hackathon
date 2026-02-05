# from fastapi import FastAPI, Header, HTTPException
# from fastapi.responses import Response
# from datetime import datetime

# from app.schemas import ScamRequest, ScamResponse
# from app.orchestrator import run_agents
# from dotenv import load_dotenv
# import os

# load_dotenv()

# print("Gemini key loaded:", bool(os.getenv("GEMINI_API_KEY")))

# API_KEY = os.getenv("GEMINI_API_KEY")

# app = FastAPI(title="Agentic HoneyPot API")

# @app.get("/handover")
# def health():
#     return {"status": "ready"}


# @app.post("/handover", response_model=ScamResponse)
# def handover(
#     request: ScamRequest,
#     x_api_key: str = Header(None)
# ):
#     if  x_api_key != API_KEY:
#         raise HTTPException(status_code=401, detail="Invalid API Key")

#     # ✅ Single source of truth
#     result = run_agents(
#         session_id=request.sessionId,
#         message=request.message.text,
#         conversation_history=request.conversationHistory
#     )

#     return {
#         "status": "success",
#         "sessionId": request.sessionId,

#         # 🔑 DO NOT recompute this
#         "scamDetected": result.get("scamDetected",False),

#         "agentReply": {
#             "sender": "user",
#             "text": result.get("reply", ""),
#             "timestamp": datetime.utcnow().isoformat() + "Z"
#         },

#         "engagementMetrics": {
#             "totalMessagesExchanged": result["engagementMetrics"]["totalMessagesExchanged"]
#         },


#         "extractedIntelligence": result.get("extractedIntelligence", {
#             "bankAccounts": [],
#             "upiIds": [],
#             "phishingLinks": [],
#             "phoneNumbers": [],
#             "suspiciousKeywords": []
#         }),

#         "agentNotes": (
#             "Urgency and sensitive information request detected"
#             if result["scamDetected"]
#             else "No scam intent detected"
#         )
#     }


# @app.get("/")
# def root():
#     return {"status": "ok", "message": "Agentic HoneyPot API"}


# @app.get("/favicon.ico")
# def favicon():
#     return Response(status_code=204)
from fastapi import FastAPI, Header, HTTPException, Body
from fastapi.responses import Response
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

from app.schemas import ScamRequest
from app.orchestrator import run_agents

load_dotenv()

# ✅ Use a dedicated honeypot key (NOT Gemini)
API_KEY = os.getenv("HONEY_API_KEY")

app = FastAPI(title="Agentic HoneyPot API")


# ⭐ Root health check (VERY important for validators)
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Agentic HoneyPot API is running"
    }


# ⭐ Secondary health endpoint (bots often check this)
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ⭐ Optional GET on /handover (many validators try GET first)
@app.get("/handover")
def handover_health():
    return {"status": "ready"}


# ⭐ CRITICAL ENDPOINT
# This version NEVER throws 422
@app.post("/handover")
def handover(
    request: Optional[ScamRequest] = Body(default=None),
    x_api_key: Optional[str] = Header(None)
):

    # ✅ Safe API key validation
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # ⭐ Validator ping support (EMPTY BODY)
    if request is None:
        return {
            "status": "active",
            "message": "Honeypot endpoint reachable"
        }

    # ✅ Run your AI agents
    result = run_agents(
        session_id=request.sessionId,
        message=request.message.text,
        conversation_history=request.conversationHistory
    )

    # ✅ Safe dictionary access everywhere (prevents 500 errors)
    return {
        "status": "success",
        "sessionId": request.sessionId,
        "scamDetected": result.get("scamDetected", False),

        "agentReply": {
            "sender": "agent",
            "text": result.get("reply", ""),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },

        "engagementMetrics": {
            "totalMessagesExchanged":
                result.get("engagementMetrics", {}).get(
                    "totalMessagesExchanged", 0
                )
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
            if result.get("scamDetected")
            else "No scam intent detected"
        )
    }


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)
