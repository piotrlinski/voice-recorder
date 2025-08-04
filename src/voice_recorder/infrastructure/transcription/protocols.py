"""
Simple, clean protocols for transcription providers.

This module defines minimal interfaces for transcription and text improvement providers.
No complex inheritance hierarchies - just simple protocols.
"""

from abc import ABC, abstractmethod
from typing import Protocol

from voice_recorder.domain.models import TranscriptionResult


class TranscriptionProvider(Protocol):
    """Protocol for audio transcription providers.
    
    Simple interface: audio file in, text out.
    """
    
    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            TranscriptionResult containing the transcribed text
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        ...


class TextProcessor(Protocol):
    """Protocol for text processing providers.
    
    Simple interface: text in, improved text out.
    """
    
    def process_text(self, text: str) -> str:
        """Process/improve the given text.
        
        Args:
            text: Original text to process
            
        Returns:
            Processed/improved text
            
        Note:
            Should return original text if processing fails
        """
        ...
    
    def is_available(self) -> bool:
        """Check if the text processor is available and ready to use.
        
        Returns:
            True if the processor is available, False otherwise
        """
        ...


class TranscriptionService(ABC):
    """High-level transcription service that coordinates providers.
    
    This is the main service that applications use. It can be composed
    with different transcription and text processing providers.
    """
    
    @abstractmethod
    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio with basic transcription only."""
        pass
    
    @abstractmethod
    def transcribe_and_improve(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio and improve the text if text processor is available."""
        pass