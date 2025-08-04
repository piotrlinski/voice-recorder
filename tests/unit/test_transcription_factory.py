"""
Unit tests for transcription factory.
"""

import pytest
from unittest.mock import Mock, patch

from src.voice_recorder.domain.models import (
    TranscriptionConfig,
    TranscriptionMode,
    OpenAITranscriptionConfig,
    LocalTranscriptionConfig,
)
from src.voice_recorder.infrastructure.transcription.simple_factory import (
    SimpleTranscriptionServiceFactory,
)
from src.voice_recorder.infrastructure.transcription.service import (
    SimpleTranscriptionService,
)


class TestSimpleTranscriptionServiceFactory:
    """Test cases for the new SimpleTranscriptionServiceFactory."""

    def test_create_service_openai(self):
        """Test creating OpenAI service with new factory."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(
                api_key="test-key", whisper_model="whisper-1"
            ),
        )

        factory = SimpleTranscriptionServiceFactory()
        service = factory.create_service(config)

        assert isinstance(service, SimpleTranscriptionService)
        assert service.transcription_provider is not None
        assert service.text_processor is None  # Basic service has no text processor

    def test_create_enhanced_service_openai(self):
        """Test creating enhanced OpenAI service with new factory."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(
                api_key="test-key", whisper_model="whisper-1"
            ),
        )

        factory = SimpleTranscriptionServiceFactory()
        service = factory.create_enhanced_service(config)

        assert isinstance(service, SimpleTranscriptionService)
        assert service.transcription_provider is not None
        assert service.text_processor is not None  # Enhanced service has text processor

    def test_create_custom_service(self):
        """Test creating custom service with specific providers."""
        from src.voice_recorder.infrastructure.transcription.providers import (
            OpenAITranscriptionProvider,
            OpenAITextProcessor,
        )

        transcription_config = OpenAITranscriptionConfig(
            api_key="test-key", whisper_model="whisper-1"
        )

        factory = SimpleTranscriptionServiceFactory()
        transcription_provider = OpenAITranscriptionProvider(transcription_config)
        text_processor = OpenAITextProcessor(transcription_config)

        service = factory.create_custom_service(transcription_provider, text_processor)

        assert isinstance(service, SimpleTranscriptionService)
        assert service.transcription_provider == transcription_provider
        assert service.text_processor == text_processor

    def test_create_transcription_provider_openai(self):
        """Test creating OpenAI transcription provider."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(
                api_key="test-key", whisper_model="whisper-1"
            ),
        )

        factory = SimpleTranscriptionServiceFactory()
        provider = factory.create_transcription_provider(config)

        from src.voice_recorder.infrastructure.transcription.providers import (
            OpenAITranscriptionProvider,
        )

        assert isinstance(provider, OpenAITranscriptionProvider)

    def test_create_text_processor_openai(self):
        """Test creating OpenAI text processor."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(
                api_key="test-key", whisper_model="whisper-1"
            ),
        )

        factory = SimpleTranscriptionServiceFactory()
        processor = factory.create_text_processor(config)

        from src.voice_recorder.infrastructure.transcription.providers import (
            OpenAITextProcessor,
        )

        assert isinstance(processor, OpenAITextProcessor)
