from typing import Dict, Optional
from datetime import datetime
from .models import Session

class SessionManager:
    def __init__(self):
        # In-memory storage for demonstration. 
        # In production, use Redis or Memcached.
        self._sessions: Dict[str, Session] = {}

    def create_session(self, jti: str, user_id: str) -> Session:
        session = Session(jti=jti, user_id=user_id)
        self._sessions[jti] = session
        return session

    def get_session(self, jti: str) -> Optional[Session]:
        return self._sessions.get(jti)

    def update_session(self, session: Session):
        session.updated_at = datetime.utcnow()
        self._sessions[session.jti] = session

    def delete_session(self, jti: str):
        if jti in self._sessions:
            del self._sessions[jti]

    def get_session_by_state(self, state: str) -> Optional[Session]:
        # This is inefficient for in-memory, but fine for MVP.
        # A real store would have a secondary index or separate mapping.
        for session in self._sessions.values():
            if session.state == state:
                return session
        return None
