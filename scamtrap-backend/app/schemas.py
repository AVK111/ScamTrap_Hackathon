from typing import List, Optional
from pydantic import BaseModel, Field


# =========================
# Incoming Request Schemas
# =========================

class Message(BaseModel):
    sender: str = Field(..., description="scammer or user")
    text: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO-8601 timestamp")


class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
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
    totalMessagesExchanged: int


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
