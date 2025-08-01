"""
Transcription service factory.

This factory creates transcription and enhancement services using the provider-based architecture
while maintaining backwards compatibility with existing code.
"""

from ...domain.interfaces import (
    TranscriptionServiceInterface,
    EnhancedTranscriptionServiceInterface,
    ConsoleInterface,
)
from ...domain.models import TranscriptionConfig, TranscriptionMode
from .providers.whisper import OpenAIWhisperProvider, LocalWhisperProvider
from .providers.composite import OpenAIEnhancedService, LocalEnhancedService


class TranscriptionServiceFactory:
    """Factory for creating transcription services using the provider-based architecture."""

    @staticmethod
    def create_service(
        config: TranscriptionConfig,
        console: ConsoleInterface | None = None,
    ) -> TranscriptionServiceInterface:
        """Create a basic transcription service."""
        if config.mode == TranscriptionMode.OPENAI:
            return OpenAIWhisperProvider(config.openai, console)
        elif config.mode == TranscriptionMode.LOCAL:
            return LocalWhisperProvider(config.local, console)
        else:
            raise ValueError(f"Unsupported transcription mode: {config.mode}")

    @staticmethod
    def create_enhanced_service(
        config: TranscriptionConfig,
        console: ConsoleInterface | None = None,
    ) -> EnhancedTranscriptionServiceInterface:
        """Create an enhanced transcription service."""
        if config.mode == TranscriptionMode.OPENAI:
            return OpenAIEnhancedService(config, console)
        elif config.mode == TranscriptionMode.LOCAL:
            return LocalEnhancedService(config, console)
        else:
            raise ValueError(f"Unsupported transcription mode: {config.mode}")

    @staticmethod
    def create_basic_service(
        config: TranscriptionConfig,
        console: ConsoleInterface | None = None
    ) -> TranscriptionServiceInterface:
        """Create a basic transcription service (alias for create_service for backwards compatibility)."""
        return TranscriptionServiceFactory.create_service(config, console)

    @staticmethod
    def create_custom_enhanced_service(
        transcription_provider: str,
        enhancement_provider: str,
        config: TranscriptionConfig,
        console: ConsoleInterface | None = None
    ) -> EnhancedTranscriptionServiceInterface:
        """Create a custom enhanced service with specific providers."""
        # This method allows for custom combinations of providers
        # Implementation would depend on the registry pattern
        raise NotImplementedError("Custom enhanced service creation not yet implemented")
