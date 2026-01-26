class RiskAgent:
    def check(self, reply: str) -> bool:
        """
        Returns True if the reply contains risky content
        """

        blocked_terms = [
            "otp",
            "cvv",
            "password",
            "pin",
            "bank account",
            "credit card"
        ]

        reply_lower = reply.lower()

        return any(term in reply_lower for term in blocked_terms)
