import json
from app.llm.gemini_client import generate


class ScamClassifierAgent:
    def classify(self, message: str, conversation_history: list):
        text = message.lower()

        # 🔒 HARD RULES — cannot be overridden by LLM
        hard_triggers = [
            "lottery",
            "won a lottery",
            "you won",
            "congratulations",
            "claim your prize",
            "bank details",
            "send your bank",
            "processing fee",
            "advance fee",
            "wire transfer",
            "urgent action required",
            "otp",
            "upi",
            "account blocked"
        ]

        for trigger in hard_triggers:
            if trigger in text:
                return {
                    "is_scam": True,
                    "scam_type": "Lottery / Financial Scam",
                    "confidence": 0.99,
                    "reasons": [f"Detected keyword: {trigger}"]
                }

        # 🧠 FALLBACK → Gemini analysis
        return self._llm_classify(message)

    def _llm_classify(self, message: str):
        prompt = f"""
You are a cybercrime analyst.

STRICT RULES:
- Return ONLY valid JSON
- NO markdown
- NO explanations
- Any lottery, prize, reward, OTP, UPI, bank request is ALWAYS a scam
- Urgency + reward = scam

JSON FORMAT (EXACT):
{{
  "is_scam": true,
  "scam_type": "Phishing Scam",
  "confidence": 0.9,
  "reasons": ["reason1", "reason2"]
}}

Message:
\"\"\"{message}\"\"\"
"""

        try:
            raw = generate(prompt).strip()

            if not raw.startswith("{"):
                raise ValueError("Non-JSON output")

            parsed = json.loads(raw)

            return {
                "is_scam": bool(parsed.get("is_scam", True)),
                "scam_type": parsed.get("scam_type", "Unknown"),
                "confidence": float(parsed.get("confidence", 0.5)),
                "reasons": parsed.get("reasons", [])
            }

        except Exception:
            return self._fallback("LLM classification failed")

    def _fallback(self, reason):
        return {
            "is_scam": True,
            "scam_type": "Unknown",
            "confidence": 0.5,
            "reasons": [reason]
        }
