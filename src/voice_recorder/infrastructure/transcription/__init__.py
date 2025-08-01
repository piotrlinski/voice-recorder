"""
Transcription module for voice recorder.

This module provides transcription services using various providers and architectures.
"""

# Base classes
from .base.base_transcription_service import BaseTranscriptionService
from .base.base_enhancement_service import BaseEnhancementService
from .base.base_enhanced_service import BaseEnhancedService

# Factory
from .factory import TranscriptionServiceFactory

# Providers
from .providers.whisper import OpenAIWhisperProvider, LocalWhisperProvider
from .providers.llm import OpenAIGPTProvider, OllamaProvider
from .providers.composite import OpenAIEnhancedService, LocalEnhancedService

__all__ = [
    # Factory
    "TranscriptionServiceFactory",
    
    # Base classes
    "BaseTranscriptionService",
    "BaseEnhancementService", 
    "BaseEnhancedService",
    
    # Providers
    "OpenAIWhisperProvider",
    "LocalWhisperProvider",
    "OpenAIGPTProvider",
    "OllamaProvider",
    "OpenAIEnhancedService",
    "LocalEnhancedService",
]
