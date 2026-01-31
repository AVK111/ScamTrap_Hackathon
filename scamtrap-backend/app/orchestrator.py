from app.agents.scam_classifier_agent import ScamClassifierAgent
from app.agents.persona_agent import PersonaAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.conversation_agent import ConversationAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.risk_agent import RiskAgent
from app.memory.memory import SessionMemory


HIGH_RISK_KEYWORDS = [
    "lottery", "won", "prize", "reward",
    "bank", "account blocked", "otp",
    "upi", "pin", "verify", "urgent"
]


def run_agents(session_id: str, message: str, conversation_history: list):

    # 1️⃣ LOAD SESSION (LIST)
    session = SessionMemory.get(session_id)

    # 2️⃣ ADD INCOMING MESSAGE
    session.append({
        "sender": "scammer",
        "text": message
    })

    # 3️⃣ CLASSIFY (NO MEMORY MUTATION)
    classification = ScamClassifierAgent().classify(message, session)
    scam_detected = classification.get("is_scam", False)

    # 4️⃣ PERSONA + STRATEGY
    persona = PersonaAgent().select_persona({
        **classification,
        "is_scam": scam_detected
    })

    strategy = StrategyAgent().decide_strategy(classification, persona)

    # 5️⃣ GENERATE REPLY
    reply = ConversationAgent().generate_reply(
        message=message,
        conversation_history=session,
        persona=persona,
        strategy=strategy
    )

    # 6️⃣ SAVE AI REPLY TO SESSION
    session.append({
        "sender": "user",
        "text": reply
    })

    SessionMemory.save(session_id, session)

    # 7️⃣ EXTRACTION
    extracted = ExtractionAgent().extract(message, session)

    if not extracted:
        extracted = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }

    # 8️⃣ RETURN (DO NOT STORE FLAGS IN SESSION)
    return {
        "sessionId": session_id,
        "reply": reply,
        "classification": classification,
        "scamDetected": scam_detected,
        "engagementMetrics": {
            "totalMessagesExchanged": len(session)
        },
        "extractedIntelligence": extracted,
        "agentNotes": (
            "High-risk scam indicators detected"
            if scam_detected else
            "No scam intent detected"
        )
    }