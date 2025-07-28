"""
OpenAI Whisper transcription service implementation.
"""

import os


from ...domain.interfaces import TranscriptionServiceInterface, ConsoleInterface
from ...domain.models import TranscriptionConfig, TranscriptionResult


class OpenAITranscriptionService(TranscriptionServiceInterface):
    """OpenAI Whisper API transcription service."""

    def __init__(self, config: TranscriptionConfig, console: ConsoleInterface | None = None):
        """Initialize OpenAI transcription service."""
        self.config = config
        self.console = console
        self.client = None
        
        try:
            import openai

            api_key = config.api_key or os.getenv("OPENAI_API_KEY")

            self.client = openai.OpenAI(api_key=api_key)
            
            if self.console:
                self.console.print_success("✅ OpenAI client initialized")
        except ImportError:
            if self.console:
                self.console.print_error("OpenAI library not available - Install with: pip install openai")
            raise RuntimeError("OpenAI library not available")
        except Exception as e:
            if self.console:
                self.console.print_error(f"OpenAI initialization failed: {e}")
            raise RuntimeError(f"OpenAI initialization failed: {e}")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using OpenAI Whisper API."""
        if not os.path.exists(audio_file_path):
            if self.console:
                self.console.print_error(f"Audio file not found: {audio_file_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            if self.console:
                self.console.print_success("🔄 Transcribing with OpenAI Whisper...")
            
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.config.model_name,
                    file=audio_file,
                    response_format="json"
                )
            
            if self.console:
                self.console.print_success("✅ OpenAI transcription completed")
            
            return TranscriptionResult(text=response.text)
            
        except Exception as e:
            if self.console:
                self.console.print_error(f"OpenAI transcription failed: {e}")
            raise RuntimeError(f"OpenAI transcription failed: {e}") 