"""
Transcription services module.

This module provides various transcription service implementations:
- OpenAI Whisper (cloud-based)
- Local Whisper (offline using OpenAI Whisper)
"""

from .factory import TranscriptionServiceFactory
from .openai_whisper_service import OpenAITranscriptionService
from .local_whisper_service import LocalWhisperTranscriptionService


class MockTranscriptionService:
    """Mock transcription service for testing."""

    def __init__(self, mock_text: str = "Test transcription"):
        self.mock_text = mock_text

    def transcribe(self, audio_file_path: str):
        """Mock transcription method."""
        from ...domain.models import TranscriptionResult
        return TranscriptionResult(
            text=self.mock_text,
            confidence=0.95,
            duration=1.0
        )


__all__ = [
    "TranscriptionServiceFactory",
    "OpenAITranscriptionService",
    "LocalWhisperTranscriptionService",
    "MockTranscriptionService",
] 