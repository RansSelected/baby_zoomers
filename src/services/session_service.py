# agent/services/session_service.py
import uuid
import time
from typing import Optional, Dict, Any

class Session:
    def __init__(self, session_id: str, user_id: str, data: Dict[str, Any] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.data = data or {}
        self.updated_at = time.time()

    def set(self, key, val):
        self.data[key] = val
        self.updated_at = time.time()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def to_dict(self):
        return {"session_id": self.session_id, "user_id": self.user_id, "data": self.data}

class SessionService:
    """
    Simple in-memory session service for the prototype.
    In production: replace with Redis or a database, or use ADK's DatabaseSessionService sample.
    """
    def __init__(self):
        self._sessions = {}

    def get_or_create(self, session_id: Optional[str], user_id: str) -> Session:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        sid = str(uuid.uuid4())
        s = Session(session_id=sid, user_id=user_id)
        self._sessions[sid] = s
        return s

    def save(self, session: Session):
        self._sessions[session.session_id] = session
