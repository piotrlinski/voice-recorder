"""
OpenAI Whisper transcription service implementation.
"""

import os

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionResult


class OpenAITranscriptionService(TranscriptionService):
    """OpenAI Whisper transcription service implementation."""

    def __init__(self, api_key: str = None ):
        """Initialize OpenAI transcription service."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
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
            import os
            
            # Check if file exists and has content
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            file_size = os.path.getsize(audio_file_path)
            print(f"Audio file size: {file_size} bytes")
            
            if file_size == 0:
                raise ValueError("Audio file is empty")
            
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