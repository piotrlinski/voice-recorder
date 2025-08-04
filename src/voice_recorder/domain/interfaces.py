"""
Domain interfaces for the voice recorder application.

This module defines all the interfaces (protocols) used throughout the application
to enable dependency injection and maintain loose coupling between components.
All interfaces follow the Interface Segregation Principle and define clear contracts
for different aspects of the voice recording functionality.
"""

from abc import ABC, abstractmethod
from typing import Any


class AudioRecorderInterface(ABC):
    """Interface for audio recording functionality.

    Defines the contract for audio recording implementations. Implementations
    should handle audio capture, session management, and file storage.
    """

    @abstractmethod
    def start_recording(self, config: Any) -> str:
        """Start recording audio.

        Args:
            config: Audio configuration with sample rate, channels, format, etc.

        Returns:
            str: Unique session ID for the recording

        Raises:
            RuntimeError: If recording cannot be started (e.g., device unavailable)
        """
        pass

    @abstractmethod
    def stop_recording(self, session_id: str) -> str | None:
        """Stop recording and return file path.

        Args:
            session_id: The session ID returned from start_recording()

        Returns:
            str | None: Path to the saved audio file, or None if recording failed
        """
        pass

    @abstractmethod
    def is_recording(self, session_id: str) -> bool:
        """Check if recording is active.

        Args:
            session_id: The session ID to check

        Returns:
            bool: True if recording is active for this session
        """
        pass


class TranscriptionServiceInterface(ABC):
    """Interface for transcription services."""

    @abstractmethod
    def transcribe(self, audio_file_path: str) -> Any:
        """Transcribe audio file to text."""
        pass


class EnhancedTranscriptionServiceInterface(ABC):
    """Interface for enhanced transcription services with LLM post-processing."""

    @abstractmethod
    def transcribe_and_enhance(self, audio_file_path: str) -> Any:
        """Transcribe audio file and enhance the text using LLM."""
        pass

    @abstractmethod
    def enhance_text(self, original_text: str) -> Any:
        """Enhance existing text using LLM."""
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

    @abstractmethod
    def clear_clipboard(self) -> bool:
        """Clear the clipboard contents."""
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
    """Interface for logging functionality."""

    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message."""
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message."""
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message."""
        pass

    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message."""
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
