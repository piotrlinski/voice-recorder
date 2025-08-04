"""
Local Whisper transcription provider.

Simple implementation that uses local Whisper models.
"""

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import LocalTranscriptionConfig, TranscriptionResult


class LocalTranscriptionProvider:
    """Local Whisper transcription provider.
    
    Simple class that implements transcription using local Whisper models.
    """
    
    def __init__(
        self, 
        config: LocalTranscriptionConfig,
        console: ConsoleInterface | None = None
    ):
        """Initialize local transcription provider.
        
        Args:
            config: Local transcription configuration
            console: Optional console for logging
            
        Raises:
            RuntimeError: If Whisper library is not available
        """
        self.config = config
        self.console = console
        
        # Initialize local Whisper model
        try:
            import whisper
            
            if console:
                console.info(f"Loading Whisper model: {config.whisper_model}")
            
            self.model = whisper.load_model(config.whisper_model.value)
            
            if console:
                console.info("Local Whisper provider initialized")
                
        except ImportError:
            error_msg = "Whisper library not available - Install with: pip install openai-whisper"
            if console:
                console.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load Whisper model: {e}"
            if console:
                console.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using local Whisper model.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            TranscriptionResult containing the transcribed text
        """
        try:
            result = self.model.transcribe(audio_file_path)
            return TranscriptionResult(text=result["text"])
            
        except Exception as e:
            error_msg = f"Local Whisper transcription failed: {e}"
            if self.console:
                self.console.error(error_msg)
            raise RuntimeError(error_msg) from e