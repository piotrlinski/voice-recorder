"""
Domain interfaces (ports) for dependency inversion.
"""

from typing import Optional, Protocol

from .models import AudioConfig, RecordingSession, TranscriptionResult


class AudioRecorder(Protocol):
    """Interface for audio recording capabilities."""

    def start_recording(self, config: AudioConfig) -> str:
        """Start recording audio and return session ID."""
        ...

    def stop_recording(self, session_id: str) -> Optional[str]:
        """Stop recording and return audio file path."""
        ...

    def is_recording(self, session_id: str) -> bool:
        """Check if recording is active."""
        ...


class TranscriptionService(Protocol):
    """Interface for audio transcription capabilities."""

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file and return result."""
        ...


class HotkeyListener(Protocol):
    """Interface for hotkey listening capabilities."""

    def start_listening(self, on_press, on_release) -> None:
        """Start listening for hotkey events."""
        ...

    def stop_listening(self) -> None:
        """Stop listening for hotkey events."""
        ...


class TextPaster(Protocol):
    """Interface for text pasting capabilities."""

    def paste_text(self, text: str, position: Optional[str] = None) -> bool:
        """Paste text at specified position."""
        ...


class SessionManager(Protocol):
    """Interface for recording session management."""

    def create_session(self) -> RecordingSession:
        """Create a new recording session."""
        ...

    def update_session(self, session: RecordingSession) -> None:
        """Update session information."""
        ...

    def get_session(self, session_id: str) -> Optional[RecordingSession]:
        """Get session by ID."""
        ...


class AudioFeedback(Protocol):
    """Interface for audio feedback capabilities."""

    def play_start_beep(self) -> None:
        """Play start recording beep."""
        ...

    def play_stop_beep(self) -> None:
        """Play stop recording beep."""
        ...
