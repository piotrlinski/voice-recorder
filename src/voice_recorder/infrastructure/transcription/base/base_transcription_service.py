"""
Base transcription service class.

This module provides the foundation for all transcription service implementations.
"""

import os
from abc import ABC, abstractmethod
from typing import Any

from voice_recorder.domain.interfaces import TranscriptionServiceInterface, ConsoleInterface
from voice_recorder.domain.models import TranscriptionResult


class BaseTranscriptionService(TranscriptionServiceInterface):
    """Base class for all transcription services."""

    def __init__(self, config: Any, console: ConsoleInterface | None = None):
        """Initialize base transcription service."""
        self.config = config
        self.console = console
        self._validate_config()
        self._initialize()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate service-specific configuration."""
        pass

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize service-specific resources."""
        pass

    @abstractmethod
    def _transcribe_audio(self, audio_file_path: str) -> str:
        """Perform the actual transcription."""
        pass

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file to text."""
        if not os.path.exists(audio_file_path):
            if self.console:
                self.console.error(f"Audio file not found: {audio_file_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        try:
            if self.console:
                self.console.info(f"Transcribing with {self.__class__.__name__}...")

            text = self._transcribe_audio(audio_file_path)

            if self.console:
                self.console.info(f"{self.__class__.__name__} transcription completed")

            return TranscriptionResult(text=text)

        except Exception as e:
            if self.console:
                self.console.error(f"{self.__class__.__name__} transcription failed: {e}")
            raise RuntimeError(f"{self.__class__.__name__} transcription failed: {e}") 