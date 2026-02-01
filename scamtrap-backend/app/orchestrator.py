from app.agents.scam_classifier_agent import ScamClassifierAgent
from app.agents.persona_agent import PersonaAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.conversation_agent import ConversationAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.risk_agent import RiskAgent
from app.memory.session_memory import SessionMemory
from datetime import datetime
import requests

HIGH_RISK_KEYWORDS = [
    "lottery", "won", "prize", "reward",
    "bank", "account blocked", "otp",
    "upi", "pin", "verify", "urgent",
    "suspended", "locked", "expired",
    "refund", "tax", "irs", "legal action"
]
def send_final_result_to_guvi(session_id: str, result: dict):
    """
    Send final results to GUVI evaluation endpoint
    MANDATORY for hackathon scoring
    """
    
    # Only send when scam is confirmed and sufficient engagement
    if not result.get("scamDetected"):
        return False
    
    # Wait for meaningful conversation (at least 5 messages)
    total_messages = result["engagementMetrics"]["totalMessagesExchanged"]
    if total_messages < 5:
        return False
    
    # Prepare GUVI-compliant payload
    payload = {
        "sessionId": session_id,
        "scamDetected": result["scamDetected"],
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": {
            "bankAccounts": result["extractedIntelligence"].get("bankAccounts", []),
            "upiIds": result["extractedIntelligence"].get("upiIds", []),
            "phishingLinks": result["extractedIntelligence"].get("phishingLinks", []),
            "phoneNumbers": result["extractedIntelligence"].get("phoneNumbers", []),
            "suspiciousKeywords": result["extractedIntelligence"].get("suspiciousKeywords", [])
        },
        "agentNotes": result.get("agentNotes", "")
    }
    
    try:
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ GUVI callback successful for session {session_id}")
            return True
        else:
            print(f"⚠️ GUVI callback returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ GUVI callback failed: {e}")
        return False

def run_agents(session_id: str, message: str, conversation_history: list):
    """
    Main orchestration function for honeypot AI.
    Maintains human-like conversation while extracting intelligence.
    """

    # 1️⃣ LOAD SESSION (SOURCE OF TRUTH)
    session = SessionMemory.get_session(session_id)

    # 2️⃣ ADD INCOMING SCAMMER MESSAGE
    session["conversation"].append({
        "sender": "scammer",
        "text": message,
        "timestamp": _get_timestamp()
    })

    # 3️⃣ CLASSIFY (READ-ONLY MEMORY)
    classification = ScamClassifierAgent().classify(
        message,
        session["conversation"]
    )

    scam_detected = classification.get("is_scam", False)

    # 4️⃣ PERSONA + STRATEGY
    persona = PersonaAgent().select_persona({
        **classification,
        "is_scam": scam_detected
    })

    strategy = StrategyAgent().decide_strategy(
        classification,
        persona,
        len(session["conversation"])  # Pass conversation length for context
    )

    # 5️⃣ GENERATE HUMAN-LIKE REPLY
    reply = ConversationAgent().generate_reply(
        message=message,
        conversation_history=session["conversation"],
        persona=persona,
        strategy=strategy
    )

    # 6️⃣ SAVE AI REPLY
    session["conversation"].append({
        "sender": "user",
        "text": reply,
        "timestamp": _get_timestamp()
    })

    # 7️⃣ EXTRACT INTELLIGENCE (from scammer's message, not our reply)
    extracted = ExtractionAgent().extract(
        message,
        session["conversation"]
    )

    if not extracted:
        extracted = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": [],
            "emailAddresses": [],
            "cryptoWallets": [],
            "remoteAccessTools": [],
            "companyNames": [],
            "paymentMethods": []
        }

    # 8️⃣ CALCULATE RISK SCORE
    risk_score = RiskAgent().calculate_risk(
        extracted,
        classification,
        session["conversation"]
    )

    # 9️⃣ ENHANCED SCAM TYPE CLASSIFICATION
    scam_type = _classify_scam_type(extracted, message, classification)

    # 🔟 GENERATE DETAILED AGENT NOTES
    agent_notes = _generate_agent_notes(
        extracted,
        risk_score,
        scam_detected,
        scam_type,
        len(session["conversation"])
    )

    # 1️⃣1️⃣ GENERATE RECOMMENDATIONS
    recommendations = _generate_recommendations(extracted, scam_type)

    # 1️⃣2️⃣ ENGAGEMENT METRICS
    engagement_metrics = _calculate_engagement_metrics(session["conversation"], session)

    # 1️⃣3️⃣ DETERMINE CONVERSATION STATE
    conversation_stage = _determine_conversation_stage(len(session["conversation"]))
    should_continue = _should_continue_conversation(risk_score, len(session["conversation"]))

    # 1️⃣4️⃣ PERSIST SESSION
    SessionMemory.save(session_id, session)

    # 1️⃣5️⃣ FINAL RESPONSE (GUVI-COMPLIANT FORMAT)
    return {
        "status": "success",  # ✅ FIXED - Added quotes
        "sessionId": session_id,
        "reply": reply,
        "classification": classification,
        "scamDetected": scam_detected,
        "scamType": scam_type,
        "riskScore": risk_score,
        "engagementMetrics": {
            "totalMessagesExchanged": engagement_metrics["totalMessagesExchanged"],
            "engagementDurationSeconds": engagement_metrics.get("timeElapsedSeconds", 0),  # ✅ GUVI required
            "scammerMessages": engagement_metrics.get("scammerMessages", 0),
            "userMessages": engagement_metrics.get("userMessages", 0),
            "averageScammerMessageLength": engagement_metrics.get("averageScammerMessageLength", 0),
            "conversationDepth": engagement_metrics.get("conversationDepth", "shallow")
        },
        "extractedIntelligence": extracted,
        "agentNotes": agent_notes,
        "recommendations": recommendations,
        "conversationStage": conversation_stage,
        "shouldContinue": should_continue
    }

def _get_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def _classify_scam_type(extracted: dict, message: str, classification: dict) -> str:
    """Enhanced scam type classification"""
    
    message_lower = message.lower()
    
    # Tech support scams
    if extracted.get("remoteAccessTools") or any(tool in message_lower for tool in 
        ["teamviewer", "anydesk", "remote", "desktop"]):
        return "Tech Support Scam"
    
    # Tax/IRS scams
    if any(keyword in message_lower for keyword in ["tax", "irs", "refund", "government", "federal"]):
        return "Tax/IRS Scam"
    
    # Banking scams
    if any(keyword in message_lower for keyword in ["account", "bank", "blocked", "suspended", "verify"]):
        return "Banking/Account Scam"
    
    # Payment/Gift card scams
    if any(keyword in message_lower for keyword in ["gift card", "itunes", "google play", "steam", "payment"]):
        return "Payment/Gift Card Scam"
    
    # Cryptocurrency scams
    if extracted.get("cryptoWallets") or any(keyword in message_lower for keyword in 
        ["crypto", "bitcoin", "ethereum", "investment", "trading"]):
        return "Cryptocurrency Scam"
    
    # Prize/Lottery scams
    if any(keyword in message_lower for keyword in ["won", "prize", "lottery", "winner", "congratulations"]):
        return "Prize/Lottery Scam"
    
    # Phishing scams
    if extracted.get("phishingLinks") or any(keyword in message_lower for keyword in 
        ["click here", "link", "verify account", "update information"]):
        return "Phishing Scam"
    
    # Romance scams
    if any(keyword in message_lower for keyword in ["love", "lonely", "relationship", "marry"]):
        return "Romance Scam"
    
    # Job/Employment scams
    if any(keyword in message_lower for keyword in ["job", "employment", "work from home", "earn money"]):
        return "Job/Employment Scam"
    
    # Default
    return classification.get("scam_type", "Unknown Scam")


def _generate_agent_notes(extracted: dict, risk_score: int, scam_detected: bool, 
                          scam_type: str, message_count: int) -> str:
    """Generate detailed agent notes"""
    
    notes = []
    
    # Risk level assessment
    if risk_score >= 80:
        notes.append("⚠️ CRITICAL: High-confidence scam detected")
    elif risk_score >= 60:
        notes.append("⚠️ WARNING: Strong scam indicators")
    elif risk_score >= 40:
        notes.append("⚠️ CAUTION: Suspicious activity detected")
    elif scam_detected:
        notes.append("ℹ️ INFO: Potential scam patterns observed")
    else:
        notes.append("✓ INFO: Monitoring conversation")
    
    # Scam type
    if scam_type and scam_type != "Unknown Scam":
        notes.append(f"📋 Type: {scam_type}")
    
    # Intelligence gathered
    intel_count = sum([
        len(extracted.get("phishingLinks", [])),
        len(extracted.get("phoneNumbers", [])),
        len(extracted.get("bankAccounts", [])),
        len(extracted.get("upiIds", [])),
        len(extracted.get("emailAddresses", [])),
        len(extracted.get("cryptoWallets", [])),
        len(extracted.get("remoteAccessTools", []))
    ])
    
    if intel_count > 0:
        notes.append(f"🔍 {intel_count} intelligence item(s) extracted")
    
    # Specific threats
    if extracted.get("phishingLinks"):
        notes.append(f"🔗 {len(extracted['phishingLinks'])} phishing link(s) detected")
    
    if extracted.get("remoteAccessTools"):
        notes.append(f"💻 Remote access requested: {', '.join(extracted['remoteAccessTools'][:2])}")
    
    if extracted.get("bankAccounts") or extracted.get("upiIds"):
        notes.append("💰 Financial information shared by scammer")
    
    if len(extracted.get("suspiciousKeywords", [])) >= 5:
        notes.append(f"🚩 {len(extracted['suspiciousKeywords'])} red flags detected")
    
    # Conversation progress
    notes.append(f"💬 {message_count} messages exchanged")
    
    return " | ".join(notes)


def _generate_recommendations(extracted: dict, scam_type: str) -> list:
    """Generate actionable recommendations"""
    
    recommendations = []
    
    # Based on extracted intelligence
    if extracted.get("phishingLinks"):
        recommendations.append("🔗 Report phishing URLs to security authorities and domain registrars")
        recommendations.append("🔗 Submit links to phishing databases (PhishTank, Google Safe Browsing)")
    
    if extracted.get("phoneNumbers"):
        recommendations.append("📞 Report phone numbers to FTC and telecom fraud divisions")
        recommendations.append("📞 Add to scam caller databases (RoboKiller, Truecaller)")
    
    if extracted.get("bankAccounts") or extracted.get("upiIds"):
        recommendations.append("💳 Report financial accounts to banking fraud departments immediately")
        recommendations.append("💳 Submit to national cybercrime cell and RBI (India) or equivalent")
    
    if extracted.get("emailAddresses"):
        recommendations.append("📧 Report email addresses to email providers for account termination")
    
    if extracted.get("cryptoWallets"):
        recommendations.append("₿ Report crypto wallets to blockchain analysis firms")
        recommendations.append("₿ Alert cryptocurrency exchanges")
    
    if extracted.get("remoteAccessTools"):
        recommendations.append("💻 Create awareness campaigns about remote access scams")
        recommendations.append("💻 Alert software vendors (TeamViewer, AnyDesk) of abuse")
    
    # Based on scam type
    if scam_type == "Tech Support Scam":
        recommendations.append("🛡️ Report to Microsoft/Apple fraud teams")
        recommendations.append("🛡️ File complaint with IC3 (Internet Crime Complaint Center)")
    
    elif scam_type == "Tax/IRS Scam":
        recommendations.append("🏛️ Report to IRS impersonation center (phishing@irs.gov)")
        recommendations.append("🏛️ File with Treasury Inspector General")
    
    elif scam_type == "Banking/Account Scam":
        recommendations.append("🏦 Alert all major banks about the scam pattern")
        recommendations.append("🏦 Submit to Anti-Phishing Working Group")
    
    # Default recommendations
    if not recommendations:
        recommendations.append("📝 Continue monitoring and gathering intelligence")
        recommendations.append("📝 Document all interactions for law enforcement")
    
    # Always add these
    recommendations.append("📊 Share intelligence with scam tracking databases")
    recommendations.append("🎯 Use data to improve scam detection algorithms")
    
    return recommendations


def _calculate_engagement_metrics(conversation: list, session: dict) -> dict:
    """Calculate detailed engagement metrics"""
    
    total_messages = len(conversation)
    scammer_messages = len([m for m in conversation if m.get("sender") == "scammer"])
    user_messages = len([m for m in conversation if m.get("sender") == "user"])
    
    # Calculate time elapsed if timestamps available
    time_elapsed = 0
    if len(conversation) >= 2:
        try:
            first_time = datetime.fromisoformat(conversation[0].get("timestamp", ""))
            last_time = datetime.fromisoformat(conversation[-1].get("timestamp", ""))
            time_elapsed = (last_time - first_time).total_seconds()
        except:
            # Fallback: use session start time if available
            if "start_time" in session:
                try:
                    time_elapsed = (datetime.now() - session["start_time"]).total_seconds()
                except:
                    pass
    
    # Average message length
    avg_scammer_length = 0
    if scammer_messages > 0:
        total_length = sum([len(m.get("text", "")) for m in conversation if m.get("sender") == "scammer"])
        avg_scammer_length = total_length / scammer_messages
    
    return {
        "totalMessagesExchanged": total_messages,
        "scammerMessages": scammer_messages,
        "userMessages": user_messages,
        "timeElapsedSeconds": int(time_elapsed),
        "averageScammerMessageLength": int(avg_scammer_length),
        "conversationDepth": "deep" if total_messages > 20 else "medium" if total_messages > 10 else "shallow"
    }


def _determine_conversation_stage(message_count: int) -> str:
    """Determine what stage the conversation is in"""
    if message_count <= 6:
        return "early"
    elif message_count <= 20:
        return "mid"
    else:
        return "late"


def _should_continue_conversation(risk_score: int, message_count: int) -> bool:
    """Determine if conversation should continue"""
    
    # Stop if very high risk and enough data gathered
    if risk_score >= 90 and message_count >= 15:
        return False
    
    # Stop if conversation is too long (prevent infinite loops)
    if message_count >= 100:
        return False
    
    # Otherwise continue
    return True