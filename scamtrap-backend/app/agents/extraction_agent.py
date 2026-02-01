import re

class ExtractionAgent:
    """
    Extracts scam intelligence from messages
    """
    
    def extract(self, message: str, conversation_history: list) -> dict:
        """
        Extract scam intelligence from messages
        
        Args:
            message: Current message text
            conversation_history: Full conversation history
            
        Returns:
            Dictionary with extracted intelligence
        """
        
        # Combine current message + recent history for context
        full_text = message
        if conversation_history:
            recent = " ".join([msg.get("text", "") for msg in conversation_history[-5:]])
            full_text = recent + " " + message
        
        extracted = {
            "bankAccounts": self._extract_bank_accounts(full_text),
            "upiIds": self._extract_upi_ids(full_text),
            "phishingLinks": self._extract_links(full_text),
            "phoneNumbers": self._extract_phone_numbers(full_text),
            "suspiciousKeywords": self._extract_keywords(full_text),
            "emailAddresses": self._extract_emails(full_text),
            "cryptoWallets": self._extract_crypto_wallets(full_text),
            "remoteAccessTools": self._extract_remote_tools(full_text),
            "companyNames": self._extract_company_names(full_text),
            "paymentMethods": self._extract_payment_methods(full_text)
        }
        
        return extracted
    
    def _extract_bank_accounts(self, text: str) -> list:
        """Extract bank account numbers"""
        # Indian account numbers: 9-18 digits
        # IBAN: 2 letters + 2 digits + up to 30 alphanumeric
        patterns = [
            r'\b\d{9,18}\b',  # Indian/standard
            r'\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b'  # IBAN
        ]
        accounts = []
        for pattern in patterns:
            accounts.extend(re.findall(pattern, text))
        return list(set(accounts))
    
    def _extract_upi_ids(self, text: str) -> list:
        """Extract UPI IDs (format: name@bank)"""
        pattern = r'\b[\w\.\-]+@(?:paytm|phonepe|gpay|okaxis|ybl|oksbi|okicici|okhdfc|ibl|axl|[\w]+)\b'
        upi_ids = re.findall(pattern, text, re.IGNORECASE)
        return list(set(upi_ids))
    
    def _extract_links(self, text: str) -> list:
        """Extract URLs and potential phishing links"""
        # URLs with protocol
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Domains without protocol
        domain_pattern = r'\b[\w-]+\.(?:com|net|org|info|biz|xyz|online|site|top|click|tk|ml|ga|cf|gq)\b'
        domains = re.findall(domain_pattern, text, re.IGNORECASE)
        
        all_links = urls + [f"http://{d}" for d in domains]
        return list(set(all_links))
    
    def _extract_phone_numbers(self, text: str) -> list:
        """Extract phone numbers"""
        patterns = [
            r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
            r'\b\d{10}\b',  # 10-digit (India/US)
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # Formatted
        ]
        numbers = []
        for pattern in patterns:
            numbers.extend(re.findall(pattern, text))
        return list(set(numbers))
    
    def _extract_emails(self, text: str) -> list:
        """Extract email addresses"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return list(set(emails))
    
    def _extract_crypto_wallets(self, text: str) -> list:
        """Extract cryptocurrency wallet addresses"""
        patterns = [
            r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',  # Bitcoin
            r'\b0x[a-fA-F0-9]{40}\b',  # Ethereum
            r'\bT[A-Za-z1-9]{33}\b'  # TRON
        ]
        wallets = []
        for pattern in patterns:
            wallets.extend(re.findall(pattern, text))
        return list(set(wallets))
    
    def _extract_remote_tools(self, text: str) -> list:
        """Extract remote access tool mentions"""
        tools = [
            "teamviewer", "anydesk", "ammyy", "supremo", "logmein",
            "chrome remote", "ultraviewer", "zoho assist", "remote desktop"
        ]
        found = [tool for tool in tools if tool in text.lower()]
        return list(set(found))
    
    def _extract_company_names(self, text: str) -> list:
        """Extract mentions of companies (often impersonated)"""
        pattern = r'\b(microsoft|amazon|google|apple|facebook|meta|paypal|netflix|irs|social security|fedex|ups|dhl|bank of america|chase|wells fargo|citibank|hdfc|icici|sbi|axis)\b'
        companies = re.findall(pattern, text, re.IGNORECASE)
        return list(set([c.title() for c in companies]))
    
    def _extract_payment_methods(self, text: str) -> list:
        """Extract payment method mentions"""
        pattern = r'(venmo|cashapp|zelle|paypal|paytm|phonepe|gpay)[\s:@]*([\w\.\-]+)?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        methods = [f"{app}:{handle}" if handle else app for app, handle in matches]
        return list(set(methods))
    
    def _extract_keywords(self, text: str) -> list:
        """Extract suspicious keywords with categories"""
        keywords = {
            "urgency": ["urgent", "immediately", "right now", "asap", "hurry", "quick", "expire", "limited time"],
            "authority": ["irs", "fbi", "police", "legal action", "arrest", "warrant", "court", "lawsuit"],
            "financial": ["refund", "tax", "prize", "lottery", "inheritance", "investment", "crypto", "bitcoin"],
            "tech_support": ["virus", "malware", "hacked", "compromised", "suspended", "blocked", "security alert"],
            "payment": ["gift card", "itunes", "google play", "steam", "amazon card", "prepaid", "wire transfer"],
            "social_engineering": ["verify", "confirm", "update", "validate", "secure", "protect", "recover"],
            "secrecy": ["don't tell", "keep secret", "confidential", "between us", "don't hang up"]
        }
        
        found = []
        text_lower = text.lower()
        
        for category, terms in keywords.items():
            for term in terms:
                if term in text_lower:
                    found.append(f"{category}:{term}")
        
        return list(set(found))