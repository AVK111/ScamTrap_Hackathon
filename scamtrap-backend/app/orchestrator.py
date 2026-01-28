from app.agents.scam_classifier_agent import ScamClassifierAgent
from app.agents.persona_agent import PersonaAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.conversation_agent import ConversationAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.risk_agent import RiskAgent
from app.memory.memory import ScamPatternMemory


# 🚨шин HARD RULES (LLM CANNOT OVERRIDE)
HIGH_RISK_KEYWORDS = [
    "lottery",
    "won",
    "prize",
    "reward",
    "bank details",
    "account blocked",
    "otp",
    "upi",
    "pin",
    "verify immediately",
    "urgent"
]


def run_agents(
    session_id: str,
    message: str,
    conversation_history: list
):
    message_lower = message.lower()

    # =========================
    # 1️⃣ RULE-BASED DETECTION
    # =========================
    rule_hit = any(keyword in message_lower for keyword in HIGH_RISK_KEYWORDS)

    # =========================
    # 2️⃣ LLM CLASSIFICATION
    # =========================
    classification = ScamClassifierAgent().classify(
        message,
        conversation_history
    )

    llm_says_scam = classification.get("is_scam", False)

    # =========================
    # 3️⃣ INTELLIGENCE EXTRACTION
    # =========================
    extracted = ExtractionAgent().extract(message,conversation_history)

    if not extracted:
        extracted = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }

    keywords = extracted.get("suspiciousKeywords", [])

    # =========================
    # 4️⃣ MEMORY UPDATE
    # =========================
    if llm_says_scam:
        ScamPatternMemory.update(
            classification.get("scam_type", "Unknown"),
            keywords
        )

    known_pattern = ScamPatternMemory.is_known_pattern(keywords)

    # =========================
    # 5️⃣ FINAL SCAM DECISION
    # =========================
    scam_detected = rule_hit or llm_says_scam or known_pattern

    # =========================
    # 6️⃣ PERSONA + STRATEGY
    # =========================
    persona = PersonaAgent().select_persona({
        **classification,
        "is_scam": scam_detected
    })

    strategy = StrategyAgent().decide_strategy(
        classification,
        persona
    )

    # =========================
    # 7️⃣ SCAMMER REPLY (OLLAMA)
    # =========================
    reply = ConversationAgent().generate_reply(
        message=message,
        conversation_history=conversation_history,
        persona=persona,
        strategy=strategy
    )

    # =========================
    # 8️⃣ RISK CHECK
    # =========================
    risk_flag = RiskAgent().check(reply)

    # =========================
    # 9️⃣ METRICS
    # =========================
    total_messages = len(conversation_history) + 1

    # =========================
    # ✅ FINAL RESPONSE
    # =========================
    return {
        "sessionId": session_id,
        "reply": reply,
        "classification": classification,
        "scamDetected": scam_detected,
        "engagementMetrics": {
            "totalMessagesExchanged": total_messages
        },
        "extractedIntelligence": extracted,
        "agentNotes": (
            "High-risk scam indicators detected"
            if scam_detected
            else "No scam intent detected"
        ),
        "risk_flag": risk_flag
    }
