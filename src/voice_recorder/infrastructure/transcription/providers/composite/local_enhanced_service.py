"""
Local enhanced transcription service.

This service combines Local Whisper for transcription and Ollama for text enhancement.
"""

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import TranscriptionConfig
from voice_recorder.infrastructure.transcription.base.base_enhanced_service import BaseEnhancedService
from voice_recorder.infrastructure.transcription.providers.whisper.local_whisper_provider import LocalWhisperProvider
from voice_recorder.infrastructure.transcription.providers.llm.ollama_provider import OllamaProvider


class LocalEnhancedService(BaseEnhancedService):
    """Local Whisper + Ollama enhanced transcription service."""

    def __init__(self, config: TranscriptionConfig, console: ConsoleInterface | None = None):
        """Initialize Local enhanced service."""
        transcription_service = LocalWhisperProvider(config.local, console)
        enhancement_service = OllamaProvider(config.local, console)
        super().__init__(transcription_service, enhancement_service, console) 