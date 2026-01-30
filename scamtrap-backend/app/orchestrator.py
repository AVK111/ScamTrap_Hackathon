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


def run_agents(
    session_id: str,
    message: str,
    conversation_history: list
):
    # 🔁 Load session memory
    session = SessionMemory.get(session_id)

    # 🧾 Append incoming scammer message
    session["conversation"].append({
        "sender": "scammer",
        "text": message
    })

    # =========================
    # 1️⃣ SCAM CLASSIFICATION
    # =========================
    classification = ScamClassifierAgent().classify(
        message,
        session["conversation"]
    )

    # Hard-rule reinforcement
    message_lower = message.lower()
    rule_hit = any(k in message_lower for k in HIGH_RISK_KEYWORDS)

    scam_detected = classification.get("is_scam", False) or rule_hit
    session["scamDetected"] = session["scamDetected"] or scam_detected

    # =========================
    # 2️⃣ PERSONA + STRATEGY
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
    # 3️⃣ AGENTIC REPLY
    # =========================
    reply = ConversationAgent().generate_reply(
        message=message,
        conversation_history=session["conversation"],
        persona=persona,
        strategy=strategy
    )

    # Append agent reply to memory
    session["conversation"].append({
        "sender": "user",
        "text": reply
    })

    # =========================
    # 4️⃣ INTELLIGENCE EXTRACTION
    # =========================
    extracted = ExtractionAgent().extract(
        message,
        session["conversation"]
    )

    for key in session["extractedIntelligence"]:
        session["extractedIntelligence"][key].extend(
            extracted.get(key, [])
        )

    # =========================
    # 5️⃣ RISK CHECK
    # =========================
    risk_flag = RiskAgent().check(reply)

    # =========================
    # 6️⃣ SAVE SESSION
    # =========================
    SessionMemory.save(session_id, session)

    # =========================
    # ✅ FINAL RESPONSE
    # =========================
    return {
        "sessionId": session_id,
        "reply": reply,
        "classification": classification,
        "scamDetected": session["scamDetected"],
        "engagementMetrics": {
            "totalMessagesExchanged": len(session["conversation"])
        },
        "extractedIntelligence": session["extractedIntelligence"],
        "agentNotes": (
            "High-risk scam indicators detected"
            if session["scamDetected"]
            else "No scam intent detected"
        ),
        "risk_flag": risk_flag
    }
