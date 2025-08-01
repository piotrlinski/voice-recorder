"""
Base enhanced service class.

This module provides the foundation for enhanced transcription services that combine
transcription and text enhancement capabilities.
"""

from typing import Any

from voice_recorder.domain.interfaces import EnhancedTranscriptionServiceInterface, ConsoleInterface
from voice_recorder.domain.models import EnhancedTranscriptionResult
from voice_recorder.infrastructure.transcription.base.base_transcription_service import BaseTranscriptionService
from voice_recorder.infrastructure.transcription.base.base_enhancement_service import BaseEnhancementService


class BaseEnhancedService(EnhancedTranscriptionServiceInterface):
    """Base class for enhanced transcription services."""

    def __init__(
        self,
        transcription_service: BaseTranscriptionService,
        enhancement_service: BaseEnhancementService,
        console: ConsoleInterface | None = None
    ):
        """Initialize base enhanced service."""
        self.transcription_service = transcription_service
        self.enhancement_service = enhancement_service
        self.console = console

    def transcribe_and_enhance(self, audio_file_path: str) -> EnhancedTranscriptionResult:
        """Transcribe audio file and enhance the text using LLM."""
        try:
            # First, transcribe the audio
            if self.console:
                self.console.info("Transcribing audio...")

            transcription_result = self.transcription_service.transcribe(audio_file_path)

            if not transcription_result or not transcription_result.text.strip():
                if self.console:
                    self.console.warning("No transcription generated")
                raise RuntimeError("No transcription generated")

            original_text = transcription_result.text

            # Then enhance the text using LLM
            if self.enhancement_service.is_available():
                provider_name = self.enhancement_service.__class__.__name__
                self.enhancement_service._log_enhancement_start(provider_name)

                enhanced_text = self.enhancement_service.enhance_text(original_text)

                self.enhancement_service._log_enhancement_complete(provider_name)

                return EnhancedTranscriptionResult(
                    original_text=original_text,
                    enhanced_text=enhanced_text,
                    confidence=transcription_result.confidence,
                    duration=transcription_result.duration,
                    enhancement_used=True,
                    gpt_model=provider_name
                )
            else:
                # Fallback to original text if enhancement service is not available
                if self.console:
                    self.console.warning("Enhancement service not available, using original text")

                return EnhancedTranscriptionResult(
                    original_text=original_text,
                    enhanced_text=original_text,
                    confidence=transcription_result.confidence,
                    duration=transcription_result.duration,
                    enhancement_used=False,
                    gpt_model=None
                )

        except Exception as e:
            if self.console:
                self.console.error(f"Enhanced transcription failed: {e}")
            raise RuntimeError(f"Enhanced transcription failed: {e}")

    def enhance_text(self, original_text: str) -> EnhancedTranscriptionResult:
        """Enhance existing text using LLM."""
        if not original_text.strip():
            if self.console:
                self.console.warning("No text provided for enhancement")
            raise ValueError("No text provided for enhancement")

        try:
            if self.enhancement_service.is_available():
                provider_name = self.enhancement_service.__class__.__name__
                self.enhancement_service._log_enhancement_start(provider_name)

                enhanced_text = self.enhancement_service.enhance_text(original_text)

                self.enhancement_service._log_enhancement_complete(provider_name)

                return EnhancedTranscriptionResult(
                    original_text=original_text,
                    enhanced_text=enhanced_text,
                    confidence=None,
                    duration=None,
                    enhancement_used=True,
                    gpt_model=provider_name
                )
            else:
                # Fallback to original text if enhancement service is not available
                if self.console:
                    self.console.warning("Enhancement service not available, using original text")

                return EnhancedTranscriptionResult(
                    original_text=original_text,
                    enhanced_text=original_text,
                    confidence=None,
                    duration=None,
                    enhancement_used=False,
                    gpt_model=None
                )

        except Exception as e:
            if self.console:
                self.console.error(f"Text enhancement failed: {e}")
            raise RuntimeError(f"Text enhancement failed: {e}") 