import requests


class ConversationAgent:
    def generate_reply(self, scam_message, persona, strategy):

        prompt = f"""
You are pretending to be a real human chatting with a scammer.

Persona:
- Role: {persona.get("role", "Victim")}
- Tone: {persona.get("tone", "Confused")}
- Behavior: {persona.get("behavior", "Cautious")}

Strategy:
- Engage: {strategy.get("engage", True)}
- Delay: {strategy.get("delay", True)}

Rules:
- Sound human
- Make small mistakes
- Ask innocent questions
- Never share OTP, CVV, passwords
- Keep scammer engaged

Scammer message:
\"\"\"{scam_message}\"\"\"
"""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:latest",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
        except Exception:
            return "Sorry beta, my network is acting strange. Can you repeat slowly?"

        data = response.json()

        reply_text = (
            data.get("response")
            or data.get("message", {}).get("content")
            or ""
        )

        if not isinstance(reply_text, str) or not reply_text.strip():
            return "Sorry, I didn't understand that... can you explain again?"

        return reply_text.strip()
