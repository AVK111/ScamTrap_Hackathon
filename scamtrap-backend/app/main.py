from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.orchestrator import run_agents
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ScamTrap Honeypot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "service": "ScamTrap Honeypot API",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "handover": "/handover",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ScamTrap Honeypot"
    }

@app.post("/handover")
async def handover(request: Request):
    """Main endpoint for scam detection and engagement"""
    try:
        data = await request.json()
        
        # Extract required fields
        session_id = data.get("sessionId")
        message = data.get("message", {})
        conversation_history = data.get("conversationHistory", [])
        
        # Validate input
        if not session_id:
            raise HTTPException(status_code=400, detail="sessionId is required")
        
        if not message or not message.get("text"):
            raise HTTPException(status_code=400, detail="message.text is required")
        
        message_text = message.get("text")
        
        # Log incoming request
        logger.info(f"📥 Session {session_id}: Received message: {message_text[:50]}...")
        
        # Process with agents
        result = run_agents(
            session_id=session_id,
            message=message_text,
            conversation_history=conversation_history
        )
        
        # Log result
        logger.info(f"📤 Session {session_id}: Scam={result['scamDetected']}, Risk={result['riskScore']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in handover: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
