from typing import Dict, List


class SessionMemory:
    """
    In-memory session store (safe for hackathon & evaluation)
    """

    _sessions: Dict[str, Dict] = {}

    @classmethod
    def get(cls, session_id: str) -> Dict:
        if session_id not in cls._sessions:
            cls._sessions[session_id] = {
                "conversation": [],
                "extractedIntelligence": {
                    "bankAccounts": [],
                    "upiIds": [],
                    "phishingLinks": [],
                    "phoneNumbers": [],
                    "suspiciousKeywords": []
                },
                "scamDetected": False
            }
        return cls._sessions[session_id]

    @classmethod
    def save(cls, session_id: str, data: Dict):
        cls._sessions[session_id] = data

    @classmethod
    def clear(cls, session_id: str):
        if session_id in cls._sessions:
            del cls._sessions[session_id]
