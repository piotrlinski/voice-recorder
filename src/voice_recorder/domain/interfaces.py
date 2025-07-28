"""
Domain interfaces for the voice recorder application.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol


class AudioRecorderInterface(ABC):
    """Interface for audio recording functionality."""

    @abstractmethod
    def start_recording(self, config: Any) -> str:
        """Start recording audio."""
        pass

    @abstractmethod
    def stop_recording(self, session_id: str) -> str | None:
        """Stop recording and return file path."""
        pass

    @abstractmethod
    def is_recording(self, session_id: str) -> bool:
        """Check if recording is active."""
        pass


class TranscriptionServiceInterface(ABC):
    """Interface for transcription services."""

    @abstractmethod
    def transcribe(self, audio_file_path: str) -> Any:
        """Transcribe audio file to text."""
        pass


class HotkeyListenerInterface(ABC):
    """Interface for hotkey listening functionality."""

    @abstractmethod
    def start_listening(self) -> None:
        """Start listening for hotkey events."""
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        """Stop listening for hotkey events."""
        pass


class TextPasterInterface(ABC):
    """Interface for text pasting functionality."""

    @abstractmethod
    def paste_text(self, text: str) -> bool:
        """Paste text at current cursor position."""
        pass


class SessionManagerInterface(ABC):
    """Interface for session management."""

    @abstractmethod
    def create_session(self, session_id: str) -> Any:
        """Create a new session."""
        pass

    @abstractmethod
    def update_session(self, session_id: str, **kwargs) -> Any:
        """Update session with new data."""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Any | None:
        """Get session by ID."""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete session by ID."""
        pass


class ConsoleInterface(ABC):
    """Interface for console output functionality."""

    @abstractmethod
    def print(self, *args, **kwargs) -> None:
        """Print to console."""
        pass

    @abstractmethod
    def print_panel(self, text: str, title: str = "", style: str = "default") -> None:
        """Print a formatted panel."""
        pass

    @abstractmethod
    def print_error(self, message: str) -> None:
        """Print error message."""
        pass

    @abstractmethod
    def print_success(self, message: str) -> None:
        """Print success message."""
        pass

    @abstractmethod
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        pass


# Legacy interfaces for backward compatibility
class AudioRecorder(AudioRecorderInterface):
    """Legacy interface for audio recording capabilities."""
    pass


class TranscriptionService(TranscriptionServiceInterface):
    """Legacy interface for audio transcription capabilities."""
    pass


class HotkeyListener(HotkeyListenerInterface):
    """Legacy interface for hotkey listening capabilities."""
    pass


class TextPaster(TextPasterInterface):
    """Legacy interface for text pasting capabilities."""
    pass


class SessionManager(SessionManagerInterface):
    """Legacy interface for recording session management."""
    pass


class AudioFeedback(ABC):
    """Interface for audio feedback capabilities."""

    @abstractmethod
    def play_start_beep(self) -> None:
        """Play start recording beep."""
        pass

    @abstractmethod
    def play_stop_beep(self) -> None:
        """Play stop recording beep."""
        pass
