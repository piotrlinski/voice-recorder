"""
Unit tests for transcription factory.
"""

from unittest.mock import Mock, patch

import pytest

from src.voice_recorder.domain.models import TranscriptionConfig, TranscriptionMode
from src.voice_recorder.infrastructure.transcription.factory import TranscriptionServiceFactory


class TestTranscriptionServiceFactory:
    """Test cases for TranscriptionServiceFactory."""

    def test_create_openai_service(self):
        """Test creating OpenAI transcription service."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER,
            model_name="whisper-1",
            api_key="test-key"
        )
        
        with patch('src.voice_recorder.infrastructure.transcription.factory.OpenAITranscriptionService') as mock_service:
            service = TranscriptionServiceFactory.create_service(config)
            mock_service.assert_called_once_with(config)

    def test_create_openai_service_without_api_key(self):
        """Test creating OpenAI service without API key."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER,
            model_name="whisper-1",
            api_key=None
        )
        
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY not set"):
            TranscriptionServiceFactory.create_service(config)

    def test_create_local_whisper_service(self):
        """Test creating Local Whisper transcription service."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.LOCAL_WHISPER,
            model_name="base"
        )
        
        with patch('src.voice_recorder.infrastructure.transcription.factory.LocalWhisperTranscriptionService') as mock_service:
            service = TranscriptionServiceFactory.create_service(config)
            mock_service.assert_called_once_with(config)

    # Note: Ollama service tests have been removed as Ollama services are no longer supported

    def test_create_unsupported_mode(self):
        """Test creating service with unsupported mode."""
        # Create a config with an invalid mode by directly setting the attribute
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER  # Start with valid mode
        )
        # Manually set an invalid mode
        config.mode = "unsupported_mode"  # type: ignore
        
        with pytest.raises(ValueError, match="Unsupported transcription mode"):
            TranscriptionServiceFactory.create_service(config) 