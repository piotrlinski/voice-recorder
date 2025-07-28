"""
Transcription service factory for creating different transcription services.
"""

from typing import Optional

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionConfig, TranscriptionMode
from .openai_service import OpenAITranscriptionService
from .local_whisper_service import LocalWhisperTranscriptionService
from .ollama_whisper_service import OllamaWhisperTranscriptionService
from .ollama_model_service import OllamaModelTranscriptionService


class TranscriptionServiceFactory:
    """Factory for creating transcription services based on configuration."""

    @staticmethod
    def create_service(config: TranscriptionConfig) -> TranscriptionService:
        """Create a transcription service based on configuration."""
        if config.mode == TranscriptionMode.OPENAI_WHISPER:
            if not config.api_key:
                raise ValueError("OpenAI API key required for OpenAI Whisper mode")
            return OpenAITranscriptionService(config.api_key)
        
        elif config.mode == TranscriptionMode.LOCAL_WHISPER:
            return LocalWhisperTranscriptionService(config.model_name)
        
        elif config.mode == TranscriptionMode.OLLAMA_WHISPER:
            return OllamaWhisperTranscriptionService(
                base_url=config.ollama_base_url
            )
        
        elif config.mode == TranscriptionMode.OLLAMA_MODEL:
            return OllamaModelTranscriptionService(
                model_name=config.model_name,
                base_url=config.ollama_base_url
            )
        
        else:
            raise ValueError(f"Unsupported transcription mode: {config.mode}") 