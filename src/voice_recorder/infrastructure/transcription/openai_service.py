"""
OpenAI Whisper transcription service implementation.
"""

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionResult


class OpenAITranscriptionService(TranscriptionService):
    """OpenAI Whisper transcription service implementation."""

    def __init__(self, api_key: str):
        """Initialize OpenAI transcription service."""
        self.api_key = api_key
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            print("OpenAI client initialized successfully")
        except ImportError:
            raise RuntimeError("openai library not available. Install with: pip install openai")
        except Exception as e:
            raise RuntimeError(f"OpenAI initialization failed: {e}")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using OpenAI Whisper (English only)."""
        try:
            import openai
            
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            
            return TranscriptionResult(
                text=response.text,
                confidence=None,  # OpenAI doesn't provide confidence scores
                duration=None,
            )
        except Exception as e:
            print(f"OpenAI transcription error: {e}")
            raise 