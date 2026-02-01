# app/agents/strategy_agent.py

class StrategyAgent:
    def decide_strategy(self, classification: dict, persona: dict, message_count: int = 0):
        """
        Decide engagement strategy based on classification, persona, and conversation stage
        
        Args:
            classification: Scam classification results
            persona: Selected persona
            message_count: Number of messages exchanged (optional)
        """
        
        scam_type = classification.get("scam_type", "unknown")
        is_scam = classification.get("is_scam", False)
        
        # Default strategy
        strategy = {
            "engage": "curious",
            "delay": "none",
            "goal": "gather_info"
        }
        
        if not is_scam:
            # Not a scam - be brief and polite
            strategy["engage"] = "polite"
            strategy["goal"] = "end_conversation"
            return strategy
        
        # Adjust strategy based on conversation stage
        if message_count <= 5:
            # Early stage - build trust
            strategy["engage"] = "confused"
            strategy["delay"] = "none"
            strategy["goal"] = "build_trust"
            
        elif message_count <= 15:
            # Mid stage - extract intelligence
            strategy["engage"] = "interested"
            strategy["delay"] = "minor"
            strategy["goal"] = "extract_intelligence"
            
        else:
            # Late stage - deep extraction or stall
            strategy["engage"] = "compliant"
            strategy["delay"] = "moderate"
            strategy["goal"] = "extract_intelligence"
        
        # Adjust based on scam type
        if scam_type in ["tech_support", "Tech Support Scam"]:
            strategy["engage"] = "confused"
            strategy["goal"] = "extract_intelligence"
            
        elif scam_type in ["banking", "Banking/Account Scam"]:
            strategy["engage"] = "worried"
            strategy["delay"] = "minor"
            
        elif scam_type in ["prize", "Prize/Lottery Scam"]:
            strategy["engage"] = "excited"
            strategy["delay"] = "none"
            
        elif scam_type in ["payment", "Payment/Gift Card Scam"]:
            strategy["engage"] = "eager"
            strategy["goal"] = "extract_intelligence"
        
        return strategy