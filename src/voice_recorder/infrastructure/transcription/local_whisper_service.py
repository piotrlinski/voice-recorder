"""
Local OpenAI Whisper transcription service implementation.
"""

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionResult


class LocalWhisperTranscriptionService(TranscriptionService):
    """Local OpenAI Whisper transcription service implementation."""

    def __init__(self, model_name: str = "base"):
        """Initialize Local Whisper transcription service."""
        self.model_name = model_name
        self.model = None
        try:
            import whisper
            # Load the model (you can specify different sizes: tiny, base, small, medium, large)
            self.model = whisper.load_model(self.model_name)
            print(f"Local Whisper model '{self.model_name}' loaded successfully")
        except ImportError:
            raise RuntimeError("openai-whisper not available. Install with: pip install openai-whisper")
        except Exception as e:
            raise RuntimeError(f"Local Whisper initialization failed: {e}")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using local Whisper."""
        if not self.model:
            raise RuntimeError("Local Whisper model not initialized")
        
        try:
            # Transcribe the audio file
            result = self.model.transcribe(audio_file_path)
            
            return TranscriptionResult(
                text=result["text"],
                confidence=None,  # Local Whisper doesn't provide confidence scores
                duration=None,
            )
        except Exception as e:
            print(f"Local transcription error: {e}")
            raise 