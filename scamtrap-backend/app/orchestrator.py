from app.agents.scam_classifier_agent import ScamClassifierAgent
from app.agents.persona_agent import PersonaAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.conversation_agent import ConversationAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.risk_agent import RiskAgent

def run_agents(scam_message: str):

    classification = ScamClassifierAgent().classify(scam_message)

    # 🚨 EARLY EXIT — NOT A SCAM
    if not classification.get("is_scam", True):
        return {
            "reply": "This message does not appear to be a scam.",
            "scam_type": "Not a Scam",
            "confidence": classification.get("confidence", 1.0),
            "reasons": classification.get("reasons", []),
            "extracted_data": [],
            "risk_flag": False
        }

    # 🟢 CONTINUE ONLY IF SCAM
    persona = PersonaAgent().select_persona(classification)
    strategy = StrategyAgent().decide_strategy(classification, persona)

    reply = ConversationAgent().generate_reply(
        scam_message=scam_message,
        persona=persona,
        strategy=strategy
    )

    extracted = ExtractionAgent().extract(scam_message)
    risk_flag = RiskAgent().check(reply)

    return {
        "reply": reply,
        "scam_type": classification["scam_type"],
        "confidence": classification["confidence"],
        "reasons": classification["reasons"],
        "extracted_data": extracted,
        "risk_flag": risk_flag
    }
