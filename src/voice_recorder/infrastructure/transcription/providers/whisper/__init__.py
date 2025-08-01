"""
Whisper transcription providers.

This module contains Whisper-based transcription service implementations.
"""

from .openai_whisper_provider import OpenAIWhisperProvider
from .local_whisper_provider import LocalWhisperProvider

__all__ = [
    "OpenAIWhisperProvider",
    "LocalWhisperProvider",
] 