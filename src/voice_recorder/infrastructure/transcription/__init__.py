"""
Transcription services module.

This module provides various transcription service implementations:
- OpenAI Whisper (cloud-based)
- Local Whisper (offline using Whisper.cpp)
- Ollama Whisper (local using Ollama)
- Ollama Models (any Ollama model)
"""

from .factory import TranscriptionServiceFactory
from .openai_service import OpenAITranscriptionService
from .local_whisper_service import LocalWhisperTranscriptionService
from .ollama_whisper_service import OllamaWhisperTranscriptionService
from .ollama_model_service import OllamaModelTranscriptionService
from .mock_service import MockTranscriptionService

__all__ = [
    "TranscriptionServiceFactory",
    "OpenAITranscriptionService",
    "LocalWhisperTranscriptionService",
    "OllamaWhisperTranscriptionService",
    "OllamaModelTranscriptionService",
    "MockTranscriptionService",
] 