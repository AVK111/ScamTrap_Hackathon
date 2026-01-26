class PersonaAgent:
    def select_persona(self, classification: dict):

        scam_type = classification.get("scam_type", "").lower()

        if "lottery" in scam_type:
            return {
                "role": "Excited but cautious winner",
                "tone": "grateful, curious",
                "behavior": "asks about delivery, taxes, delays payment"
            }

        if "bank" in scam_type:
            return {
                "role": "Worried bank customer",
                "tone": "confused, anxious",
                "behavior": "asks for clarification, delays action"
            }

        if "job" in scam_type:
            return {
                "role": "Hopeful job applicant",
                "tone": "enthusiastic but unsure",
                "behavior": "asks about hiring process and fees"
            }

        if "crypto" in scam_type:
            return {
                "role": "Skeptical investor",
                "tone": "technical, cautious",
                "behavior": "asks for proof and documentation"
            }

        return {
            "role": "Normal user",
            "tone": "polite",
            "behavior": "asks generic questions"
        }
