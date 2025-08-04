"""
Clean transcription and text processing providers.

This module contains simple implementations of transcription and text processing
providers without complex inheritance hierarchies.
"""

# Transcription providers
from .openai_transcription import OpenAITranscriptionProvider
from .local_transcription import LocalTranscriptionProvider

# Text processing providers
from .openai_text_processor import OpenAITextProcessor
from .ollama_text_processor import OllamaTextProcessor
from .no_text_processor import NoTextProcessor

__all__ = [
    # Transcription providers
    "OpenAITranscriptionProvider",
    "LocalTranscriptionProvider",
    # Text processing providers
    "OpenAITextProcessor",
    "OllamaTextProcessor",
    "NoTextProcessor",
]
