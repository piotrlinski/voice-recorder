"""
Unit tests for session manager components.
"""

from datetime import datetime

import pytest

from src.voice_recorder.domain.models import RecordingSession, RecordingState
from src.voice_recorder.infrastructure.session_manager import InMemorySessionManager


class TestInMemorySessionManager:
    """Test cases for InMemorySessionManager."""

    def test_init(self):
        """Test InMemorySessionManager initialization."""
        manager = InMemorySessionManager()
        assert manager.sessions == {}

    def test_create_session(self):
        """Test session creation."""
        manager = InMemorySessionManager()
        session = manager.create_session()

        assert isinstance(session, RecordingSession)
        assert session.id is not None
        assert session.start_time is not None
        assert session.state == RecordingState.IDLE
        assert session.id in manager.sessions

    def test_update_session(self):
        """Test session update."""
        manager = InMemorySessionManager()
        session = manager.create_session()

        # Update the session
        session.state = RecordingState.RECORDING
        manager.update_session(session)

        updated_session = manager.get_session(session.id)
        assert updated_session.state == RecordingState.RECORDING

    def test_get_session_existing(self):
        """Test getting existing session."""
        manager = InMemorySessionManager()
        session = manager.create_session()

        retrieved_session = manager.get_session(session.id)
        assert retrieved_session == session

    def test_get_session_non_existing(self):
        """Test getting non-existing session."""
        manager = InMemorySessionManager()
        session = manager.get_session("non_existing_id")
        assert session is None

    def test_get_all_sessions(self):
        """Test getting all sessions."""
        manager = InMemorySessionManager()
        session1 = manager.create_session()
        session2 = manager.create_session()

        all_sessions = manager.get_all_sessions()
        assert len(all_sessions) == 2
        assert session1 in all_sessions
        assert session2 in all_sessions

    def test_delete_session_existing(self):
        """Test deleting existing session."""
        manager = InMemorySessionManager()
        session = manager.create_session()

        result = manager.delete_session(session.id)
        assert result is True
        assert session.id not in manager.sessions

    def test_delete_session_non_existing(self):
        """Test deleting non-existing session."""
        manager = InMemorySessionManager()
        result = manager.delete_session("non_existing_id")
        assert result is False

    def test_clear_sessions(self):
        """Test clearing all sessions."""
        manager = InMemorySessionManager()
        manager.create_session()
        manager.create_session()

        assert len(manager.sessions) == 2
        manager.clear_sessions()
        assert len(manager.sessions) == 0


class MockSessionManager:
    """Mock session manager for testing."""

    def __init__(self):
        self.sessions = []
        self.create_count = 0
        self.update_count = 0
        self.get_count = 0
        self.delete_count = 0
        self.clear_count = 0

    def create_session(self) -> RecordingSession:
        """Create a new recording session."""
        self.create_count += 1
        session_id = f"mock_session_{self.create_count}"
        session = RecordingSession(
            id=session_id, start_time=datetime.now(), state=RecordingState.IDLE
        )
        self.sessions.append(session)
        return session

    def update_session(self, session: RecordingSession) -> None:
        """Update session information."""
        self.update_count += 1
        for i, existing_session in enumerate(self.sessions):
            if existing_session.id == session.id:
                self.sessions[i] = session
                break

    def get_session(self, session_id: str):
        """Get session by ID."""
        self.get_count += 1
        for session in self.sessions:
            if session.id == session_id:
                return session
        return None

    def get_all_sessions(self):
        """Get all sessions."""
        return list(self.sessions)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        self.delete_count += 1
        for i, session in enumerate(self.sessions):
            if session.id == session_id:
                del self.sessions[i]
                return True
        return False

    def clear_sessions(self) -> None:
        """Clear all sessions."""
        self.clear_count += 1
        self.sessions.clear()


class TestMockSessionManager:
    """Test cases for MockSessionManager."""

    def test_init(self):
        """Test MockSessionManager initialization."""
        manager = MockSessionManager()
        assert manager.sessions == []
        assert manager.create_count == 0
        assert manager.update_count == 0

    def test_create_session(self):
        """Test mock session creation."""
        manager = MockSessionManager()
        session = manager.create_session()

        assert isinstance(session, RecordingSession)
        assert session.id == "mock_session_1"
        assert session.state == RecordingState.IDLE
        assert len(manager.sessions) == 1
        assert manager.create_count == 1

    def test_create_multiple_sessions(self):
        """Test creating multiple mock sessions."""
        manager = MockSessionManager()
        session1 = manager.create_session()
        session2 = manager.create_session()

        assert session1.id == "mock_session_1"
        assert session2.id == "mock_session_2"
        assert manager.create_count == 2
        assert len(manager.sessions) == 2

    def test_update_session(self):
        """Test mock session update."""
        manager = MockSessionManager()
        session = manager.create_session()

        # Update the session
        session.state = RecordingState.RECORDING
        manager.update_session(session)

        assert manager.update_count == 1
        updated_session = manager.get_session(session.id)
        assert updated_session.state == RecordingState.RECORDING

    def test_get_session_existing(self):
        """Test getting existing mock session."""
        manager = MockSessionManager()
        session = manager.create_session()

        retrieved_session = manager.get_session(session.id)
        assert retrieved_session == session

    def test_get_session_non_existing(self):
        """Test getting non-existing mock session."""
        manager = MockSessionManager()
        session = manager.get_session("non_existing_id")
        assert session is None

    def test_session_state_transitions(self):
        """Test session state transitions."""
        manager = InMemorySessionManager()
        session = manager.create_session()

        # Initial state
        assert session.state == RecordingState.IDLE

        # Transition to recording
        session.state = RecordingState.RECORDING
        manager.update_session(session)
        assert manager.get_session(session.id).state == RecordingState.RECORDING

        # Transition to processing
        session.state = RecordingState.PROCESSING
        manager.update_session(session)
        assert manager.get_session(session.id).state == RecordingState.PROCESSING

        # Transition to error
        session.state = RecordingState.ERROR
        manager.update_session(session)
        assert manager.get_session(session.id).state == RecordingState.ERROR

        # Back to idle
        session.state = RecordingState.IDLE
        manager.update_session(session)
        assert manager.get_session(session.id).state == RecordingState.IDLE
