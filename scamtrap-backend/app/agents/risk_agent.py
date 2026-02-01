class RiskAgent:
    """
    Calculates risk score based on extracted intelligence and conversation patterns
    """
    
    def calculate_risk(self, extracted: dict, classification: dict, conversation: list) -> int:
        """
        Calculate risk score from 0-100 based on multiple factors
        
        Args:
            extracted: Extracted intelligence dictionary
            classification: Scam classification results
            conversation: Full conversation history
            
        Returns:
            Risk score (0-100)
        """
        
        score = 0
        
        # 1. BASE SCAM DETECTION (30 points max)
        if classification.get("is_scam", False):
            score += 30
        
        # 2. HIGH-RISK INTELLIGENCE (40 points max)
        # Phishing links - very dangerous
        if extracted.get("phishingLinks"):
            score += min(len(extracted["phishingLinks"]) * 15, 20)
        
        # Remote access tools - critical threat
        if extracted.get("remoteAccessTools"):
            score += 25
        
        # Financial data - high risk
        if extracted.get("bankAccounts"):
            score += min(len(extracted["bankAccounts"]) * 10, 15)
        
        if extracted.get("upiIds"):
            score += min(len(extracted["upiIds"]) * 10, 15)
        
        if extracted.get("cryptoWallets"):
            score += min(len(extracted["cryptoWallets"]) * 10, 15)
        
        # 3. MEDIUM-RISK INTELLIGENCE (20 points max)
        # Phone numbers
        if extracted.get("phoneNumbers"):
            score += min(len(extracted["phoneNumbers"]) * 3, 10)
        
        # Email addresses
        if extracted.get("emailAddresses"):
            score += min(len(extracted["emailAddresses"]) * 2, 5)
        
        # Payment methods
        if extracted.get("paymentMethods"):
            score += min(len(extracted["paymentMethods"]) * 3, 8)
        
        # 4. SUSPICIOUS KEYWORDS (10 points max)
        keyword_count = len(extracted.get("suspiciousKeywords", []))
        if keyword_count >= 10:
            score += 10
        elif keyword_count >= 5:
            score += 7
        elif keyword_count >= 3:
            score += 4
        
        # 5. URGENCY TACTICS (10 points max)
        urgency_keywords = [
            kw for kw in extracted.get("suspiciousKeywords", [])
            if any(urgent in kw.lower() for urgent in ["urgency:", "urgent", "immediate", "now", "hurry"])
        ]
        if len(urgency_keywords) >= 3:
            score += 10
        elif len(urgency_keywords) >= 2:
            score += 5
        
        # 6. IMPERSONATION (15 points max)
        if extracted.get("companyNames"):
            # Scammer impersonating legitimate companies
            score += min(len(extracted["companyNames"]) * 5, 15)
        
        # 7. CONVERSATION PATTERN ANALYSIS (10 points bonus)
        pattern_score = self._analyze_conversation_patterns(conversation)
        score += pattern_score
        
        # Cap at 100
        return min(score, 100)
    
    def _analyze_conversation_patterns(self, conversation: list) -> int:
        """
        Analyze conversation for scam patterns
        Returns: 0-10 points
        """
        
        if not conversation or len(conversation) < 2:
            return 0
        
        score = 0
        scammer_messages = [msg for msg in conversation if msg.get("sender") == "scammer"]
        
        if not scammer_messages:
            return 0
        
        # Check for rapid-fire messages (pressure tactic)
        if len(scammer_messages) >= 5:
            score += 3
        
        # Check for long messages (detailed scam scripts)
        avg_length = sum(len(msg.get("text", "")) for msg in scammer_messages) / len(scammer_messages)
        if avg_length > 100:
            score += 2
        
        # Check for question avoidance (scammer ignoring user questions)
        user_questions = sum(1 for msg in conversation if msg.get("sender") == "user" and "?" in msg.get("text", ""))
        if user_questions >= 3:
            score += 2
        
        # Check for repeated demands
        scammer_texts = [msg.get("text", "").lower() for msg in scammer_messages]
        repeated_phrases = self._find_repeated_phrases(scammer_texts)
        if repeated_phrases >= 2:
            score += 3
        
        return min(score, 10)
    
    def _find_repeated_phrases(self, texts: list) -> int:
        """Count how many times key phrases are repeated"""
        
        key_phrases = [
            "verify", "confirm", "urgent", "immediately", "account", 
            "blocked", "suspended", "click", "link", "payment"
        ]
        
        repeated_count = 0
        for phrase in key_phrases:
            count = sum(1 for text in texts if phrase in text)
            if count >= 2:
                repeated_count += 1
        
        return repeated_count
    
    def get_risk_level(self, risk_score: int) -> str:
        """
        Convert numeric risk score to human-readable level
        
        Args:
            risk_score: Score from 0-100
            
        Returns:
            Risk level string
        """
        
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def get_threat_indicators(self, extracted: dict) -> list:
        """
        Get list of specific threat indicators found
        
        Args:
            extracted: Extracted intelligence
            
        Returns:
            List of threat descriptions
        """
        
        threats = []
        
        if extracted.get("phishingLinks"):
            threats.append(f"Phishing links detected ({len(extracted['phishingLinks'])})")
        
        if extracted.get("remoteAccessTools"):
            threats.append(f"Remote access tool requested: {', '.join(extracted['remoteAccessTools'])}")
        
        if extracted.get("bankAccounts"):
            threats.append(f"Bank accounts exposed ({len(extracted['bankAccounts'])})")
        
        if extracted.get("upiIds"):
            threats.append(f"UPI IDs shared ({len(extracted['upiIds'])})")
        
        if extracted.get("cryptoWallets"):
            threats.append(f"Cryptocurrency wallets detected ({len(extracted['cryptoWallets'])})")
        
        if len(extracted.get("suspiciousKeywords", [])) >= 5:
            threats.append(f"Multiple red flags ({len(extracted['suspiciousKeywords'])} keywords)")
        
        if extracted.get("companyNames"):
            threats.append(f"Impersonating: {', '.join(extracted['companyNames'][:3])}")
        
        return threats