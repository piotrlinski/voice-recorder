"""
Local OpenAI Whisper transcription service implementation.
"""

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionResult


class LocalWhisperTranscriptionService(TranscriptionService):
    """Local OpenAI Whisper transcription service implementation."""

    def __init__(self, config):
        """Initialize Local Whisper transcription service."""
        self.model_name = config.model_name
        self.model = None
        try:
            import whisper
            import warnings
            
            # Suppress FP16 warning
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
                # Load the model
                self.model = whisper.load_model(self.model_name)
            
            print(f"Local Whisper model '{self.model_name}' loaded successfully (FP32)")
        except ImportError:
            raise RuntimeError("openai-whisper not available. Install with: pip install openai-whisper")
        except Exception as e:
            raise RuntimeError(f"Local Whisper initialization failed: {e}")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using local Whisper."""
        if not self.model:
            raise RuntimeError("Local Whisper model not initialized")
        
        try:
            import warnings
            
            # Suppress FP16 warning during transcription
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
                # Transcribe the audio file with FP32 precision
                result = self.model.transcribe(audio_file_path, fp16=False)
            
            return TranscriptionResult(
                text=result["text"],
                confidence=None,  # Local Whisper doesn't provide confidence scores
                duration=None,
            )
        except Exception as e:
            print(f"Local transcription error: {e}")
            raise 