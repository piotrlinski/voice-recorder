"""
Local Whisper transcription service implementation.
"""

import os
from typing import Optional

from ...domain.interfaces import TranscriptionServiceInterface, ConsoleInterface
from ...domain.models import TranscriptionConfig, TranscriptionResult


class LocalWhisperTranscriptionService(TranscriptionServiceInterface):
    """Local Whisper transcription service."""

    def __init__(self, config: TranscriptionConfig, console: ConsoleInterface | None = None):
        """Initialize local Whisper transcription service."""
        self.config = config
        self.console = console
        self.model = None
        
        try:
            import whisper
            self.model = whisper.load_model(config.model_name)
            
            if self.console:
                self.console.print_success("✅ Local Whisper model loaded")
        except ImportError:
            if self.console:
                self.console.print_error("Whisper library not available - Install with: pip install openai-whisper")
            raise RuntimeError("Whisper library not available")
        except Exception as e:
            if self.console:
                self.console.print_error(f"Whisper model loading failed: {e}")
            raise RuntimeError(f"Whisper model loading failed: {e}")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using local Whisper model."""
        if not os.path.exists(audio_file_path):
            if self.console:
                self.console.print_error(f"Audio file not found: {audio_file_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            if self.console:
                self.console.print_success("🔄 Transcribing with local Whisper...")
            
            # Transcribe using local Whisper
            result = self.model.transcribe(
                audio_file_path,
                language="en",  # English only
                fp16=False  # Use FP32 for better compatibility
            )
            
            if self.console:
                self.console.print_success("✅ Local Whisper transcription completed")
            
            return TranscriptionResult(text=result["text"])
            
        except Exception as e:
            if self.console:
                self.console.print_error(f"Local Whisper transcription failed: {e}")
            raise RuntimeError(f"Local Whisper transcription failed: {e}") 