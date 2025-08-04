"""
Session manager infrastructure implementations.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from ..domain.models import RecordingSession, RecordingState
from ..domain.interfaces import ConsoleInterface


class InMemorySessionManager:
    """In-memory session manager implementation."""

    def __init__(self, console: Optional[ConsoleInterface] = None):
        self.sessions: Dict[str, RecordingSession] = {}
        self.console = console

    def create_session(self) -> RecordingSession:
        """Create a new recording session."""
        session_id = str(uuid.uuid4())
        session = RecordingSession(
            id=session_id, start_time=datetime.now(), state=RecordingState.IDLE
        )
        self.sessions[session_id] = session
        if self.console:
            self.console.debug(f"Created session with ID: {session_id}")
        return session

    def update_session(self, session: RecordingSession) -> None:
        """Update session information."""
        # Handle case where session ID might have changed
        # First, check if we can find the session by ID
        if session.id in self.sessions:
            self.sessions[session.id] = session
        else:
            # If not found by ID, it might be an ID change scenario
            # Find session by checking all sessions and update
            old_key = None
            for key, stored_session in self.sessions.items():
                if (stored_session.start_time == session.start_time and 
                    stored_session.state != RecordingState.COMPLETED):
                    # This is likely the same session with a changed ID
                    old_key = key
                    break
            
            if old_key:
                # Remove old entry and add with new ID
                del self.sessions[old_key]
                self.sessions[session.id] = session
            else:
                # This is a new session, just add it
                self.sessions[session.id] = session

    def get_session(self, session_id: str) -> Optional[RecordingSession]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        if self.console:
            if session:
                self.console.debug(f"Found session {session_id}: state={session.state}")
            else:
                self.console.debug(f"Session {session_id} not found. Available sessions: {list(self.sessions.keys())}")
        return session

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
