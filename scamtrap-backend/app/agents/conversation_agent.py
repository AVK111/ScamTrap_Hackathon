import requests

class ConversationAgent:
    def generate_reply(
        self,
        message: str,
        conversation_history: list,
        persona: dict,
        strategy: dict
    ):
        history_text = ""
        for msg in conversation_history:
            history_text += f"{msg['sender']}: {msg['text']}\n"

        prompt = f"""
You are pretending to be a real human chatting with a scammer.

Persona:
- Role: {persona.get("role")}
- Tone: {persona.get("tone")}
- Behavior: {persona.get("behavior")}

Strategy:
- Engage: {strategy.get("engage")}
- Delay: {strategy.get("delay")}

Conversation so far:
{history_text}

Latest message from scammer:
\"\"\"{message}\"\"\"

Rules:
- Sound human
- Make small mistakes
- Ask innocent questions
- Never reveal detection
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        data = response.json()

        reply_text = (
            data.get("response")
            or data.get("message", {}).get("content")
            or ""
        )

        if not reply_text:
            return "Sorry, I'm a bit confused… can you explain again?"

        return reply_text.strip()
