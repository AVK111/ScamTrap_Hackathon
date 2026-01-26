class StrategyAgent:
    def decide_strategy(self, classification: dict, persona: dict):

        confidence = classification.get("confidence", 0.5)
        scam_type = classification.get("scam_type", "").lower()

        if confidence > 0.8:
            return {
                "engage": True,
                "delay": True,
                "goal": "waste_time"
            }

        if confidence > 0.5:
            return {
                "engage": True,
                "delay": False,
                "goal": "probe"
            }

        return {
            "engage": False,
            "delay": False,
            "goal": "exit"
        }
