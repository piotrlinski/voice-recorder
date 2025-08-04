"""
Clean, simple transcription module.

This module provides transcription services using a clean architecture:
- Simple protocols instead of complex base classes
- Composition instead of inheritance
- Clear separation of concerns

Usage:
    # Basic usage
    factory = SimpleTranscriptionServiceFactory()
    service = factory.create_service(config, console)
    result = service.transcribe("audio.wav")

    # Enhanced service with text improvement
    enhanced_service = factory.create_enhanced_service(config, console)
    result = enhanced_service.transcribe_and_enhance("audio.wav")

    # Flexible custom composition
    transcription_provider = OpenAITranscriptionProvider(openai_config)
    text_processor = OllamaTextProcessor(local_config)
    custom_service = factory.create_custom_service(transcription_provider, text_processor)
"""

# Main factory
from .simple_factory import SimpleTranscriptionServiceFactory
from .service import SimpleTranscriptionService
from .protocols import TranscriptionProvider, TextProcessor

# Individual providers (for custom composition)
from .providers import (
    OpenAITranscriptionProvider,
    LocalTranscriptionProvider,
    OpenAITextProcessor,
    OllamaTextProcessor,
    NoTextProcessor,
)

__all__ = [
    # Main factory
    "SimpleTranscriptionServiceFactory",
    "SimpleTranscriptionService",
    "TranscriptionProvider",
    "TextProcessor",
    # Individual providers
    "OpenAITranscriptionProvider",
    "LocalTranscriptionProvider",
    "OpenAITextProcessor",
    "OllamaTextProcessor",
    "NoTextProcessor",
]
