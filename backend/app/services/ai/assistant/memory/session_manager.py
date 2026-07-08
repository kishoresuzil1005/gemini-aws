import uuid

class SessionManager:
    def __init__(self):
        self.active_sessions = {}

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {"user_id": user_id, "active": True}
        return session_id

    def get_session(self, session_id: str):
        return self.active_sessions.get(session_id)

    def end_session(self, session_id: str):
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["active"] = False
