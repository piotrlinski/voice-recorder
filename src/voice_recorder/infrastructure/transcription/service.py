"""
Simple transcription service implementation.

This service composes transcription and text processing providers without
complex inheritance hierarchies.
"""

import os
from typing import Optional

from voice_recorder.domain.interfaces import (
    ConsoleInterface,
    TranscriptionServiceInterface,
    EnhancedTranscriptionServiceInterface,
)
from voice_recorder.domain.models import TranscriptionResult
from .protocols import TranscriptionProvider, TextProcessor


class SimpleTranscriptionService(TranscriptionServiceInterface, EnhancedTranscriptionServiceInterface):
    """Simple transcription service using composition instead of inheritance.
    
    This service coordinates a transcription provider and an optional text processor.
    It's much simpler than the previous base class hierarchy.
    """
    
    def __init__(
        self,
        transcription_provider: TranscriptionProvider,
        text_processor: Optional[TextProcessor] = None,
        console: Optional[ConsoleInterface] = None
    ):
        """Initialize the transcription service.
        
        Args:
            transcription_provider: Provider that transcribes audio to text
            text_processor: Optional provider that improves text quality
            console: Optional console for logging
        """
        self.transcription_provider = transcription_provider
        self.text_processor = text_processor
        self.console = console
    
    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            TranscriptionResult with transcribed text
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        if not os.path.exists(audio_file_path):
            error_msg = f"Audio file not found: {audio_file_path}"
            if self.console:
                self.console.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            if self.console:
                provider_name = self.transcription_provider.__class__.__name__
                self.console.info(f"Transcribing with {provider_name}...")
            
            result = self.transcription_provider.transcribe(audio_file_path)
            
            if self.console:
                self.console.info("Transcription completed")
            
            return result
            
        except Exception as e:
            error_msg = f"Transcription failed: {e}"
            if self.console:
                self.console.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def transcribe_and_enhance(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file and improve the text if text processor is available.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            TranscriptionResult with original text and optionally improved text
        """
        # First transcribe the audio
        result = self.transcribe(audio_file_path)
        
        # Then try to improve the text if we have a text processor
        if self.text_processor and self.text_processor.is_available():
            try:
                if self.console:
                    processor_name = self.text_processor.__class__.__name__
                    self.console.info(f"Improving text with {processor_name}...")
                
                improved_text = self.text_processor.process_text(result.text)
                
                if self.console:
                    self.console.info("Text improvement completed")
                
                # Create a new result with the improved text
                # We'll add an improved_text field to TranscriptionResult if needed
                # For now, just replace the text
                return TranscriptionResult(
                    text=improved_text,
                    confidence=result.confidence,
                    duration=result.duration
                )
                
            except Exception as e:
                if self.console:
                    self.console.warning(f"Text improvement failed: {e}, using original text")
                return result
        
        # No text processor available or not working, return original result
        if self.console and self.text_processor:
            self.console.info("Text processor not available, using original transcription")
        
        return result
    
    def enhance_text(self, original_text: str) -> TranscriptionResult:
        """Enhance existing text using text processor.
        
        Args:
            original_text: Original text to enhance
            
        Returns:
            TranscriptionResult with enhanced text
        """
        if not original_text.strip():
            return TranscriptionResult(text=original_text)
        
        if self.text_processor and self.text_processor.is_available():
            try:
                if self.console:
                    processor_name = self.text_processor.__class__.__name__
                    self.console.info(f"Enhancing text with {processor_name}...")
                
                enhanced_text = self.text_processor.process_text(original_text)
                
                if self.console:
                    self.console.info("Text enhancement completed")
                
                return TranscriptionResult(text=enhanced_text)
                
            except Exception as e:
                if self.console:
                    self.console.warning(f"Text enhancement failed: {e}, using original text")
                return TranscriptionResult(text=original_text)
        
        # No text processor available
        if self.console:
            self.console.info("Text processor not available, returning original text")
        
        return TranscriptionResult(text=original_text)