"""
OpenAI enhanced transcription service.

This service combines OpenAI Whisper for transcription and OpenAI GPT for text enhancement.
"""

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import TranscriptionConfig
from voice_recorder.infrastructure.transcription.base.base_enhanced_service import BaseEnhancedService
from voice_recorder.infrastructure.transcription.providers.whisper.openai_whisper_provider import OpenAIWhisperProvider
from voice_recorder.infrastructure.transcription.providers.llm.openai_gpt_provider import OpenAIGPTProvider


class OpenAIEnhancedService(BaseEnhancedService):
    """OpenAI Whisper + GPT enhanced transcription service."""

    def __init__(self, config: TranscriptionConfig, console: ConsoleInterface | None = None):
        """Initialize OpenAI enhanced service."""
        transcription_service = OpenAIWhisperProvider(config.openai, console)
        enhancement_service = OpenAIGPTProvider(config.openai, console)
        super().__init__(transcription_service, enhancement_service, console) 