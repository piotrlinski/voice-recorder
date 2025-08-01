"""
Local Whisper transcription provider implementation.
"""

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import LocalTranscriptionConfig
from voice_recorder.infrastructure.transcription.base.base_transcription_service import BaseTranscriptionService


class LocalWhisperProvider(BaseTranscriptionService):
    """Local Whisper transcription provider."""

    def __init__(
        self,
        config: LocalTranscriptionConfig,
        console: ConsoleInterface | None = None,
    ):
        """Initialize local Whisper transcription provider."""
        super().__init__(config, console)

    def _validate_config(self) -> None:
        """Validate local Whisper configuration."""
        if not self.config.whisper_model:
            raise ValueError("Whisper model size required")

    def _initialize(self) -> None:
        """Initialize local Whisper model."""
        try:
            import whisper
            model_size = self.config.whisper_model.value
            self.model = whisper.load_model(model_size)
            
            if self.console:
                self.console.info(f"Local Whisper model loaded: {model_size}")
        except ImportError:
            if self.console:
                self.console.error(
                    "Whisper library not available - Install with: pip install openai-whisper"
                )
            raise RuntimeError("Whisper library not available")
        except Exception as e:
            if self.console:
                self.console.error(f"Whisper model loading failed: {e}")
            raise RuntimeError(f"Whisper model loading failed: {e}")

    def _transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file using local Whisper model."""
        result = self.model.transcribe(
            audio_file_path,
            language="en",  # English only
            fp16=False,  # Use FP32 for better compatibility
        )
        return result["text"] 