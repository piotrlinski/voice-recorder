"""
OpenAI Whisper transcription provider implementation.
"""

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import OpenAITranscriptionConfig
from voice_recorder.infrastructure.transcription.base.base_transcription_service import BaseTranscriptionService


class OpenAIWhisperProvider(BaseTranscriptionService):
    """OpenAI Whisper API transcription provider."""

    def __init__(
        self,
        config: OpenAITranscriptionConfig,
        console: ConsoleInterface | None = None,
    ):
        """Initialize OpenAI Whisper transcription provider."""
        super().__init__(config, console)

    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.config.api_key:
            raise ValueError("OpenAI API key required")

    def _initialize(self) -> None:
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.config.api_key)
            
            if self.console:
                self.console.info("OpenAI Whisper client initialized")
        except ImportError:
            if self.console:
                self.console.error(
                    "OpenAI library not available - Install with: pip install openai"
                )
            raise RuntimeError("OpenAI library not available")
        except Exception as e:
            if self.console:
                self.console.error(f"OpenAI initialization failed: {e}")
            raise RuntimeError(f"OpenAI initialization failed: {e}")

    def _transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file using OpenAI Whisper API."""
        with open(audio_file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model=self.config.whisper_model,
                file=audio_file,
                response_format="json",
            )
        return response.text 