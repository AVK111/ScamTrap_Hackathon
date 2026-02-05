from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# =========================
# Incoming Request Schemas
# =========================

class Message(BaseModel):
    sender: str = Field(default="scammer", description="scammer or user")
    text: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO-8601 timestamp"
    )


class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[dict] = None


# =========================
# Outgoing Response Schemas
# =========================

class AgentReply(BaseModel):
    sender: str = "user"

    # 🔐 CRITICAL FIX:
    # text is OPTIONAL with a default empty string
    # so FastAPI NEVER crashes
    text: Optional[str] = ""

    timestamp: str


class EngagementMetrics(BaseModel):
    totalMessagesExchanged: int = Field(...,example=4)


class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []


class ScamResponse(BaseModel):
    status: str
    sessionId: str
    scamDetected: bool

    # 🧠 Reply is OPTIONAL but structured
    agentReply: Optional[AgentReply]

    engagementMetrics: EngagementMetrics
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str
