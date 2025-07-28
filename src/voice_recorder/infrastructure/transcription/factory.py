"""
Transcription service factory for creating different transcription services.
"""

from typing import Optional

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionConfig, TranscriptionMode
from .openai_whisper_service import OpenAITranscriptionService
from .local_whisper_service import LocalWhisperTranscriptionService


class TranscriptionServiceFactory:
    """Factory for creating transcription services based on configuration."""

    @staticmethod
    def create_service(config: TranscriptionConfig) -> TranscriptionService:
        """Create a transcription service based on configuration."""
        if config.mode == TranscriptionMode.OPENAI_WHISPER:
            return OpenAITranscriptionService(config)
        
        elif config.mode == TranscriptionMode.LOCAL_WHISPER:
            return LocalWhisperTranscriptionService(config)
        
        else:
            raise ValueError(f"Unsupported transcription mode: {config.mode}") 