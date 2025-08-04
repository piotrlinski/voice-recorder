"""
OpenAI Whisper transcription provider.

Simple implementation that follows the TranscriptionProvider protocol.
"""

import os

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import OpenAITranscriptionConfig, TranscriptionResult


class OpenAITranscriptionProvider:
    """OpenAI Whisper transcription provider.
    
    Simple class that implements transcription using OpenAI's Whisper API.
    No complex base classes or inheritance.
    """
    
    def __init__(
        self, 
        config: OpenAITranscriptionConfig,
        console: ConsoleInterface | None = None
    ):
        """Initialize OpenAI transcription provider.
        
        Args:
            config: OpenAI transcription configuration
            console: Optional console for logging
            
        Raises:
            ValueError: If API key is missing
            RuntimeError: If OpenAI library is not available
        """
        self.config = config
        self.console = console
        
        # Validate configuration
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI client
        try:
            import openai
            self.client = openai.OpenAI(api_key=config.api_key)
            
            if console:
                console.info("OpenAI Whisper provider initialized")
                
        except ImportError:
            error_msg = "OpenAI library not available - Install with: pip install openai"
            if console:
                console.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to initialize OpenAI client: {e}"
            if console:
                console.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using OpenAI Whisper API.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            TranscriptionResult containing the transcribed text
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        # Check if file exists first
        if not os.path.exists(audio_file_path):
            error_msg = f"Audio file not found: {audio_file_path}"
            if self.console:
                self.console.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.config.whisper_model,
                    file=audio_file,
                    response_format="json",
                )
            
            return TranscriptionResult(text=response.text)
            
        except Exception as e:
            error_msg = f"OpenAI transcription failed: {e}"
            if self.console:
                self.console.error(error_msg)
            raise RuntimeError(error_msg) from e