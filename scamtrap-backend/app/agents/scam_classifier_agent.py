import requests
import json


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
            "urgent action required"
        ]

        for trigger in hard_triggers:
            if trigger in text:
                return {
                    "is_scam": True,
                    "scam_type": "Lottery / Advance Fee Scam",
                    "confidence": 0.99,
                    "reasons": [f"Detected keyword: {trigger}"]
                }

        # 🧠 FALLBACK → LLM analysis
        return self._llm_classify(message)

    def _llm_classify(self, message: str):
        payload = {
            "model": "llama3.2:latest",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a cybercrime analyst.\n"
                        "Rules:\n"
                        "- Any lottery, prize, or reward message is ALWAYS a scam.\n"
                        "- Any request for bank details, OTP, PIN, or payment is ALWAYS a scam.\n"
                        "- Urgency + reward = scam.\n"
                        "Return ONLY valid JSON. No explanations."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Analyze the message and return JSON ONLY in this format:\n\n"
                        "{\n"
                        '  "is_scam": true,\n'
                        '  "scam_type": "Lottery Scam",\n'
                        '  "confidence": 0.95,\n'
                        '  "reasons": ["reason1", "reason2"]\n'
                        "}\n\n"
                        f"Message:\n{message}"
                    )
                }
            ],
            "stream": False
        }

        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json=payload,
                timeout=60
            )
            print("\n================ RAW OLLAMA RESPONSE ================")
            print(response.text)
            print("=====================================================\n")
        except Exception:
            return self._fallback("LLM request failed")

        data = response.json()

        content = data.get("message", {}).get("content", "").strip()

        if not content.startswith("{"):
            return self._fallback("Model did not return JSON")

        try:
            parsed = json.loads(content)
        except Exception:
            return self._fallback("Invalid JSON from model")

        return {
            "is_scam": parsed.get("is_scam", True),
            "scam_type": parsed.get("scam_type", "Unknown"),
            "confidence": float(parsed.get("confidence", 0.5)),
            "reasons": parsed.get("reasons", [])
        }

    def _fallback(self, reason):
        return {
            "is_scam": True,
            "scam_type": "Unknown",
            "confidence": 0.5,
            "reasons": [reason]
        }
