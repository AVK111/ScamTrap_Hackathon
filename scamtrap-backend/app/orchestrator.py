from app.agents.scam_classifier_agent import ScamClassifierAgent
from app.agents.persona_agent import PersonaAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.conversation_agent import ConversationAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.risk_agent import RiskAgent


def run_agents(
    session_id: str,
    message,  # Message object
    conversation_history: list
):
    # 1️⃣ Scam classification
    classification = ScamClassifierAgent().classify(
        message,
        conversation_history
    )

    # Decide scamDetected (GUVI logic)
    scam_detected = (
        classification.get("is_scam", False)
        and classification.get("confidence", 0) >= 0.7
    )

    # 2️⃣ Persona + strategy only if scam
    persona = None
    strategy = None
    reply = None

    if scam_detected:
        persona = PersonaAgent().select_persona(classification)
        strategy = StrategyAgent().decide_strategy(classification, persona)

        reply = ConversationAgent().generate_reply(
            message=message,
            conversation_history=conversation_history,
            persona=persona,
            strategy=strategy
        )
        if not reply:
            reply = "Sorry, can you explain again?"

    # 3️⃣ Intelligence extraction
    extracted = ExtractionAgent().extract(
        message,
        conversation_history
    ) or {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    }
    # Strong scam indicators (GUVI-aligned)
    STRONG_SCAM_KEYWORDS = {
        "otp", "verify", "blocked", "urgent", "account",
        "upi", "bank", "immediately", "suspended"
    }

    # Normalize keywords
    found_keywords = set(
        k.lower() for k in extracted.get("suspiciousKeywords", [])
    )

    # Final scam decision (HYBRID)
    scam_detected = (
        classification.get("is_scam", False)
        or len(found_keywords.intersection(STRONG_SCAM_KEYWORDS)) >= 2
    )


    # 4️⃣ Engagement metrics
    total_messages = len(conversation_history) + 1

    # 5️⃣ Final GUVI-compliant response
    return {
        "status": "success",
        "sessionId": session_id,
        "reply":reply,
        "scamDetected": scam_detected,
        "engagementMetrics": {
            "totalMessagesExchanged": total_messages
        },
        "extractedIntelligence": extracted,
        "agentNotes": (
            "Urgency and sensitive information request detected"
            if scam_detected else
            "No scam intent detected"
        )
    }
