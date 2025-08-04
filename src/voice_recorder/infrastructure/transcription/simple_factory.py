"""
Simple transcription service factory.

This factory creates transcription services using the new clean architecture
without complex inheritance hierarchies.
"""

from typing import Optional

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import TranscriptionConfig, TranscriptionMode

from .protocols import TranscriptionProvider, TextProcessor
from .service import SimpleTranscriptionService
from .providers import (
    OpenAITranscriptionProvider,
    LocalTranscriptionProvider,
    OpenAITextProcessor,
    OllamaTextProcessor,
    NoTextProcessor,
)


class SimpleTranscriptionServiceFactory:
    """Simple factory for creating transcription services.

    This factory creates services by composing providers instead of
    using complex inheritance hierarchies.
    """

    @staticmethod
    def create_transcription_provider(
        config: TranscriptionConfig, console: Optional[ConsoleInterface] = None
    ) -> TranscriptionProvider:
        """Create a transcription provider based on configuration.

        Args:
            config: Transcription configuration
            console: Optional console for logging

        Returns:
            Appropriate transcription provider

        Raises:
            ValueError: If transcription mode is not supported
        """
        if config.mode == TranscriptionMode.OPENAI:
            return OpenAITranscriptionProvider(config.openai, console)
        elif config.mode == TranscriptionMode.LOCAL:
            return LocalTranscriptionProvider(config.local, console)
        else:
            raise ValueError(f"Unsupported transcription mode: {config.mode}")

    @staticmethod
    def create_text_processor(
        config: TranscriptionConfig, console: Optional[ConsoleInterface] = None
    ) -> TextProcessor:
        """Create a text processor based on configuration.

        Args:
            config: Transcription configuration
            console: Optional console for logging

        Returns:
            Appropriate text processor
        """
        if config.mode == TranscriptionMode.OPENAI:
            # Use OpenAI GPT for text processing
            return OpenAITextProcessor(config.openai, console)
        elif config.mode == TranscriptionMode.LOCAL:
            # Use Ollama for text processing
            return OllamaTextProcessor(config.local, console)
        else:
            # Default to no processing
            return NoTextProcessor(console)

    @staticmethod
    def create_service(
        config: TranscriptionConfig, console: Optional[ConsoleInterface] = None
    ) -> SimpleTranscriptionService:
        """Create a basic transcription service (transcription only).

        Args:
            config: Transcription configuration
            console: Optional console for logging

        Returns:
            Transcription service with transcription provider only
        """
        transcription_provider = (
            SimpleTranscriptionServiceFactory.create_transcription_provider(
                config, console
            )
        )

        return SimpleTranscriptionService(
            transcription_provider=transcription_provider,
            text_processor=None,  # No text processing for basic service
            console=console,
        )

    @staticmethod
    def create_enhanced_service(
        config: TranscriptionConfig, console: Optional[ConsoleInterface] = None
    ) -> SimpleTranscriptionService:
        """Create an enhanced transcription service (transcription + text improvement).

        Args:
            config: Transcription configuration
            console: Optional console for logging

        Returns:
            Transcription service with both transcription and text processing
        """
        transcription_provider = (
            SimpleTranscriptionServiceFactory.create_transcription_provider(
                config, console
            )
        )
        text_processor = SimpleTranscriptionServiceFactory.create_text_processor(
            config, console
        )

        return SimpleTranscriptionService(
            transcription_provider=transcription_provider,
            text_processor=text_processor,
            console=console,
        )

    @staticmethod
    def create_custom_service(
        transcription_provider: TranscriptionProvider,
        text_processor: Optional[TextProcessor] = None,
        console: Optional[ConsoleInterface] = None,
    ) -> SimpleTranscriptionService:
        """Create a custom transcription service with specific providers.

        This allows for flexible composition of different providers.

        Args:
            transcription_provider: Provider for audio transcription
            text_processor: Optional provider for text improvement
            console: Optional console for logging

        Returns:
            Custom composed transcription service
        """
        return SimpleTranscriptionService(
            transcription_provider=transcription_provider,
            text_processor=text_processor,
            console=console,
        )
