"""
Mock transcription service for testing purposes.
"""

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionResult


class MockTranscriptionService(TranscriptionService):
    """Mock transcription service for testing."""

    def __init__(self, mock_text: str = "This is a mock transcription result"):
        """Initialize mock transcription service."""
        self.mock_text = mock_text

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Return mock transcription result."""
        return TranscriptionResult(
            text=self.mock_text,
            confidence=0.95,
            duration=1.0,
        ) 