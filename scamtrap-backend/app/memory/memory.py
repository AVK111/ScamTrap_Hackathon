class SessionMemory:
    _store = {}

    @classmethod
    def get(cls, session_id: str):
        """
        Returns conversation history list for a session.
        Creates a new one if session does not exist.
        """
        if session_id not in cls._store:
            cls._store[session_id] = []
        return cls._store[session_id]

    @classmethod
    def save(cls, session_id: str, conversation: list):
        """
        Saves updated conversation history.
        """
        cls._store[session_id] = conversation
