"""
Transcription service factory.
"""

from ...domain.interfaces import TranscriptionServiceInterface, ConsoleInterface
from ...domain.models import TranscriptionConfig, TranscriptionMode
from .local_whisper_service import LocalWhisperTranscriptionService
from .openai_whisper_service import OpenAITranscriptionService


class TranscriptionServiceFactory:
    """Factory for creating transcription services."""

    @staticmethod
    def create_service(config: TranscriptionConfig, console: ConsoleInterface | None = None) -> TranscriptionServiceInterface:
        """Create a transcription service based on configuration."""
        if config.mode == TranscriptionMode.LOCAL_WHISPER:
            return LocalWhisperTranscriptionService(config, console=console)
        elif config.mode == TranscriptionMode.OPENAI_WHISPER:
            return OpenAITranscriptionService(config, console=console)
        else:
            raise ValueError(f"Unsupported transcription mode: {config.mode}") 