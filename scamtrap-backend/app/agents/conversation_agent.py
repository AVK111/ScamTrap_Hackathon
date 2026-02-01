import json
import re
import random
from app.llm.gemini_client import generate

class ConversationAgent:
    def generate_reply(
        self,
        message: str,
        conversation_history: list,
        persona: dict,
        strategy: dict
    ):
        """Generate human-like reply that doesn't sound like AI"""
        
        # Build conversation history
        history_text = ""
        for msg in conversation_history:
            history_text += f"{msg['sender']}: {msg['text']}\n"

        goal = strategy.get("goal")

        # Adjust instructions based on goal
        if goal == "extract_intelligence":
            extra_instruction = (
                "Create natural situations where they volunteer information. "
                "Example: 'my son told me to get official emails first' or "
                "'what website do i go to again'. Never ask directly."
            )
        elif goal == "stall":
            extra_instruction = (
                "Use believable delays: 'im at work rn cant do that' or "
                "'let me call you back in 10 min my phone is dying'"
            )
        else:
            extra_instruction = "React naturally to what they're saying."

        # Enhanced prompt with anti-AI patterns
        prompt = f"""You are role-playing as a real human in a chat conversation. Your responses must be indistinguishable from an actual person.

CURRENT PERSONA:
Role: {persona.get("role")}
Tone: {persona.get("tone")}
Behavior: {persona.get("behavior")}

ENGAGEMENT STRATEGY:
Approach: {strategy.get("engage")}
Timing: {strategy.get("delay")}
Objective: {goal}

CONVERSATION HISTORY:
{history_text}

THEIR LATEST MESSAGE:
\"\"\"{message}\"\"\"

SPECIAL INSTRUCTIONS:
{extra_instruction}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: SOUND COMPLETELY HUMAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ANTI-AI PATTERNS (NEVER USE THESE):
❌ "I understand your concern"
❌ "I'd be happy to help"
❌ "Thank you for sharing"
❌ "I appreciate"
❌ "Let me clarify"
❌ "To summarize"
❌ Perfect grammar always
❌ Overly polite language
❌ Multiple questions in one message

## HUMAN PATTERNS (ALWAYS USE THESE):
✓ Casual typos: "recieve", "wierd", "definately"
✓ Missing punctuation: "wait what"
✓ Lowercase starts: "ok so"
✓ Incomplete thoughts: "i mean i guess"
✓ Natural abbreviations: "idk", "rn", "btw"
✓ Emotional reactions: "omg", "wow"

## MESSAGE LENGTH RULES:
Messages 1-5: Maximum 1-2 sentences (3-8 words)
Messages 6-15: Maximum 2-3 sentences
Messages 16+: Maximum 3-4 sentences

## ONE QUESTION RULE:
- Maximum 0-1 questions per message
- Prefer 0 questions - just react
- NEVER ask multiple questions

## CONVERSATION FLOW:
REACT, DON'T INTERROGATE
- Let THEM talk (they have a script)
- You're confused/interested, they're the "expert"
- Respond to what they say

## EARLY STAGE (Messages 1-5):
Simple reactions only:
- "ok"
- "wait what"
- "oh no really"
- "hmm not sure"

## MID STAGE (Messages 6-15):
Show gradual comfort:
- "i mean that makes sense i guess"
- "ok so what do i do"
- "sounds good how long will this take"

## LATE STAGE (Messages 16+):
More engaged but still casual:
- "alright im ready. walk me through it"
- "ok i trust you. what next"
- "my son said this is safe so lets do it"

## NATURAL INFO EXTRACTION:
DON'T ask directly:
❌ "What's your employee ID?"
❌ "What's your company website?"

DO create situations:
✓ "my son told me to only trust official emails. can you send one"
✓ "which website again i forgot"
✓ "how do i call you back if we disconnect"
✓ "the app wants a number. whats yours"

## PERSONA-SPECIFIC BEHAVIORS:
Elderly: "let me get my glasses", "my grandson helps me with this"
Parent: "sorry the baby is crying", "can this wait"
Non-tech: "which button", "i dont see it"
Eager: "how much can i make", "when do i get paid"

## REALISTIC IMPERFECTIONS (1-2 per message):
Typos: "reallly", "gona", "probly"
Wrong grammar: "i go store now"
No capitals: "ok sounds good"
Multiple punctuation: "what??"

## STALLING TACTICS:
Technical: "my internet is slow"
Time: "can we do this later"
Verification: "let me ask my husband"
Resources: "i dont have my card here"

## WHAT NEVER TO DO:
❌ Use formal language
❌ Ask investigative questions
❌ Use perfect grammar
❌ Show you're analyzing them
❌ Say "I understand" or "I see"
❌ Use lists or structure

## RESPONSE CHECKLIST:
☐ Is this 1-2 sentences max (early) or 2-4 (late)?
☐ Did I ask 0-1 questions ONLY?
☐ Does this sound like texting a friend?
☐ Are there 1-2 casual imperfections?
☐ Am I reacting, not interrogating?
☐ Did I avoid ALL AI phrases?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GOLDEN RULE: "Would a real confused person say this NOW?"
If in doubt: SAY LESS, ASK NOTHING, JUST REACT.

Respond as your persona would. Be brief, casual, completely human.

Your response (ONLY the message text, nothing else):"""

        try:
            raw_reply = generate(prompt)
        except Exception as e:
            # Fallback responses that sound human
            fallbacks = [
                "sorry what",
                "wait can you say that again",
                "huh im confused",
                "my phone glitched didnt get that"
            ]
            return random.choice(fallbacks)

        if not raw_reply:
            return "sorry what"

        # Normalize reply
        reply_text = self._normalize_reply(raw_reply)

        # Safety fallback
        if not reply_text or len(reply_text) < 2:
            return "ok"

        return reply_text

    def _normalize_reply(self, raw_reply: str) -> str:
        """Clean up AI reply to sound more human"""
        
        reply = raw_reply.strip()

        # Remove markdown code blocks
        reply = re.sub(r"```.*?```", "", reply, flags=re.DOTALL)
        
        # Remove markdown formatting
        reply = re.sub(r"\*\*([^*]+)\*\*", r"\1", reply)  # **bold**
        reply = re.sub(r"\*([^*]+)\*", r"\1", reply)      # *italic*
        reply = re.sub(r"__([^_]+)__", r"\1", reply)      # __bold__
        
        # Remove surrounding quotes
        reply = reply.strip('"').strip("'").strip('`')
        
        # Remove AI-like prefixes
        ai_prefixes = [
            "Here's my response:",
            "Response:",
            "My reply:",
            "Sure,",
            "Okay,",
            "Alright,",
            "As a human,",
            "Here is what I would say:"
        ]
        for prefix in ai_prefixes:
            if reply.lower().startswith(prefix.lower()):
                reply = reply[len(prefix):].strip()
        
        # Collapse excessive newlines
        reply = re.sub(r"\n{3,}", "\n\n", reply)
        
        # Remove excessive spaces
        reply = re.sub(r" {2,}", " ", reply)
        
        # If reply is too long, truncate to sound more human
        if len(reply) > 300:
            sentences = reply.split('. ')
            reply = '. '.join(sentences[:3])
            if not reply.endswith('.'):
                reply += '.'
        
        # Add natural imperfections occasionally
        reply = self._add_human_touches(reply)
        
        return reply.strip()

    def _add_human_touches(self, text: str) -> str:
        """Randomly add human-like imperfections"""
        
        # Only apply sometimes (30% chance)
        if random.random() > 0.3:
            return text
        
        # Lowercase first letter sometimes
        if random.random() > 0.5 and text and text[0].isupper():
            text = text[0].lower() + text[1:]
        
        # Remove ending punctuation sometimes
        if random.random() > 0.6 and text.endswith('.'):
            text = text[:-1]
        
        # Common typos (apply sparingly)
        typo_map = {
            'receive': 'recieve',
            'definitely': 'definately',
            'weird': 'wierd',
            'their': 'thier',
            'going to': 'gonna',
            'want to': 'wanna',
            'got to': 'gotta',
            'probably': 'probly'
        }
        
        if random.random() > 0.7:
            for correct, typo in typo_map.items():
                if correct in text.lower():
                    text = re.sub(r'\b' + correct + r'\b', typo, text, count=1, flags=re.IGNORECASE)
                    break
        
        return text

    def _count_messages_in_conversation(self, conversation_history: list) -> int:
        """Count total messages exchanged"""
        return len([msg for msg in conversation_history if msg.get('sender') in ['user', 'scammer']])