import re

class ExtractionAgent:
    def extract(self, message, conversation_history: list):
        """
        Extract scam intelligence from the message and conversation.
        """

        text=message.lower()
        extracted = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }

        # Example simple keyword extraction (you can improve later)
        if "upi" in text:
            extracted["suspiciousKeywords"].append("upi")

        if "otp" in text:
            extracted["suspiciousKeywords"].append("otp")

        if "http" in text or "www" in text:
            extracted["phisingLinks"].append("detected-link")

        return extracted
