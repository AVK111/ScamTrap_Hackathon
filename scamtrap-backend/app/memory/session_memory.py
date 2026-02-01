from datetime import datetime

sessions = {}

class SessionMemory:
    @staticmethod
    def get_session(session_id: str):
        """Get or create session with start_time tracking"""
        if session_id not in sessions:
            sessions[session_id] = {
                "conversation": [],
                "start_time": datetime.now()  # ✅ Track when conversation started
            }
        return sessions[session_id]
    
    @staticmethod
    def save(session_id: str, session: dict):
        """Save session state"""
        sessions[session_id] = session
    
    @staticmethod
    def clear_session(session_id: str):
        """Clear a specific session"""
        if session_id in sessions:
            del sessions[session_id]
    
    @staticmethod
    def clear_all():
        """Clear all sessions"""
        sessions.clear()