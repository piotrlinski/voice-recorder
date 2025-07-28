"""
Session manager infrastructure implementations.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from ..domain.models import RecordingSession, RecordingState


class InMemorySessionManager:
    """In-memory session manager implementation."""

    def __init__(self):
        self.sessions: Dict[str, RecordingSession] = {}

    def create_session(self) -> RecordingSession:
        """Create a new recording session."""
        session_id = str(uuid.uuid4())
        session = RecordingSession(
            id=session_id, start_time=datetime.now(), state=RecordingState.IDLE
        )
        self.sessions[session_id] = session
        return session

    def update_session(self, session: RecordingSession) -> None:
        """Update session information."""
        if session.id in self.sessions:
            self.sessions[session.id] = session

    def get_session(self, session_id: str) -> Optional[RecordingSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> List[RecordingSession]:
        """Get all sessions."""
        return list(self.sessions.values())

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def clear_sessions(self) -> None:
        """Clear all sessions."""
        self.sessions.clear()






