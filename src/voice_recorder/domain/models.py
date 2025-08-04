"""
Domain models for the voice recorder application.

This module contains all the data models used throughout the application,
including configuration models, recording session models, and transcription
result models. All models use Pydantic for data validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RecordingState(str, Enum):
    """Recording state enumeration.

    Represents the various states a recording session can be in during its lifecycle.

    Attributes:
        IDLE: Session is created but no recording has started
        RECORDING: Audio is currently being recorded
        PROCESSING: Recording finished, transcription in progress
        COMPLETED: Transcription completed successfully
        ERROR: An error occurred during recording or processing
    """

    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class AudioFormat(str, Enum):
    """Audio format enumeration."""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"


class TranscriptionMode(str, Enum):
    """Transcription mode enumeration."""

    OPENAI = "openai"
    LOCAL = "local"


class LocalWhisperModel(str, Enum):
    """Local Whisper model options."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class HotkeyConfig(BaseModel):
    """Hotkey configuration for recording controls."""

    key: str = Field(description="Primary key for the hotkey")
    modifiers: List[str] = Field(
        default_factory=list, description="Modifier keys (ctrl, alt, shift, etc.)"
    )
    description: str = Field(description="Human-readable description of the hotkey")


class OpenAITranscriptionConfig(BaseModel):
    """OpenAI transcription configuration (Whisper + GPT)."""

    api_key: Optional[str] = Field(
        default=None, description="OpenAI API key for both Whisper and GPT"
    )
    whisper_model: str = Field(
        default="whisper-1", description="OpenAI Whisper model (hard-coded)"
    )
    gpt_model: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI GPT model for enhancement (hard-coded)",
    )
    gpt_creativity: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="GPT creativity/temperature level for text improvement",
    )
    enhanced_transcription_prompt: str = Field(
        default="Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary.",
        description="Custom prompt for enhanced transcription with GPT",
    )


class LocalTranscriptionConfig(BaseModel):
    """Local transcription configuration (Local Whisper + Ollama)."""

    whisper_model: LocalWhisperModel = Field(
        default=LocalWhisperModel.SMALL, description="Local Whisper model size"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama API base URL"
    )
    ollama_model: str = Field(
        default="llama3.1", description="Ollama model for text enhancement"
    )
    ollama_creativity: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Ollama creativity/temperature level for text improvement",
    )
    enhanced_transcription_prompt: str = Field(
        default="Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary.",
        description="Custom prompt for enhanced transcription with GPT",
    )


class TranscriptionConfig(BaseModel):
    """Voice transcription configuration (both basic and enhanced)."""

    mode: TranscriptionMode = Field(
        default=TranscriptionMode.OPENAI,
        description="Transcription mode: openai or local",
    )
    openai: OpenAITranscriptionConfig = Field(
        default_factory=OpenAITranscriptionConfig,
        description="OpenAI transcription configuration",
    )
    local: LocalTranscriptionConfig = Field(
        default_factory=LocalTranscriptionConfig,
        description="Local transcription configuration",
    )


class AudioConfig(BaseModel):
    """Audio recording settings."""

    sample_rate: int = Field(default=16000, description="Sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    format: AudioFormat = Field(default=AudioFormat.WAV, description="Audio format")
    chunk_size: int = Field(default=1024, description="Audio chunk size")


class RecordingSession(BaseModel):
    """Represents a recording session."""

    id: str = Field(description="Unique session identifier")
    start_time: datetime = Field(description="Recording start time")
    end_time: Optional[datetime] = Field(default=None, description="Recording end time")
    audio_file_path: Optional[str] = Field(
        default=None, description="Path to audio file"
    )
    duration: Optional[float] = Field(
        default=None, description="Recording duration in seconds"
    )
    state: RecordingState = Field(
        default=RecordingState.IDLE, description="Current state"
    )
    transcript: Optional[str] = Field(default=None, description="Transcribed text")
    confidence: Optional[float] = Field(
        default=None, description="Transcription confidence"
    )


class TranscriptionResult(BaseModel):
    """Result of audio transcription (English only)."""

    text: str = Field(description="Transcribed text")
    confidence: Optional[float] = Field(default=None, description="Confidence score")
    duration: Optional[float] = Field(default=None, description="Audio duration")


class EnhancedTranscriptionResult(BaseModel):
    """Result of enhanced transcription with GPT post-processing."""

    original_text: str = Field(description="Original transcribed text")
    enhanced_text: str = Field(description="GPT-improved text")
    confidence: Optional[float] = Field(
        default=None, description="Original transcription confidence"
    )
    duration: Optional[float] = Field(default=None, description="Audio duration")
    enhancement_used: bool = Field(
        default=True, description="Whether GPT improvement was applied"
    )
    gpt_model: Optional[str] = Field(default=None, description="GPT model used")


class ControlsConfig(BaseModel):
    """Recording controls configuration."""

    basic_key: str = Field(description="Key to trigger basic transcription")
    enhanced_key: str = Field(
        description="Key to trigger enhanced transcription with GPT improvement"
    )


class GeneralConfig(BaseModel):
    """General application settings."""

    auto_paste: bool = Field(default=True, description="Auto-paste transcribed text")


class ApplicationConfig(BaseModel):
    """Application configuration with nested transcription modes.

    Main configuration model that contains all settings for the voice recorder
    application including transcription providers, hotkey controls, audio settings,
    and general application behavior.

    Attributes:
        transcription: Transcription service configuration (OpenAI or local)
        controls: Hotkey configuration for basic and enhanced recording
        audio: Audio recording settings (sample rate, format, etc.)
        general: General application settings (auto-paste, etc.)

    Example:
        >>> config = ApplicationConfig(
        ...     transcription=TranscriptionConfig(mode=TranscriptionMode.OPENAI),
        ...     controls=ControlsConfig(basic_key="shift_r", enhanced_key="ctrl_l"),
        ...     general=GeneralConfig(auto_paste=True)
        ... )
        >>> print(config.transcription.mode)
        openai
    """

    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    controls: ControlsConfig = Field(
        default=ControlsConfig(basic_key="shift_r", enhanced_key="ctrl_l")
    )
    audio: AudioConfig = Field(default_factory=AudioConfig)
    general: GeneralConfig = Field(default_factory=GeneralConfig)

    # Backwards compatibility properties for existing code
    @property
    def audio_config(self) -> AudioConfig:
        """Backwards compatibility: Use audio instead."""
        return self.audio

    @property
    def openai(self) -> OpenAITranscriptionConfig:
        """Backwards compatibility: Access OpenAI config from transcription."""
        return self.transcription.openai

    @property
    def transcription_config(self):
        """Backwards compatibility: Create wrapper with enhanced_config."""

        # Create a wrapper that includes enhanced_config for backwards compatibility
        class TranscriptionConfigWrapper:
            def __init__(self, config: TranscriptionConfig):
                self._config = config
                self._enhanced_config = EnhancedTranscriptionConfig()
                # Set the temperature from appropriate creativity setting based on mode
                if config.mode == TranscriptionMode.OPENAI:
                    self._enhanced_config._creativity = config.openai.gpt_creativity
                else:
                    self._enhanced_config._creativity = config.local.ollama_creativity

            @property
            def mode(self):
                # Map new modes to old modes for backwards compatibility
                if self._config.mode == TranscriptionMode.OPENAI:
                    from enum import Enum

                    class OldTranscriptionMode(str, Enum):
                        OPENAI_WHISPER = "openai_whisper"
                        LOCAL_WHISPER = "local_whisper"

                    return OldTranscriptionMode.OPENAI_WHISPER
                else:
                    from enum import Enum

                    class OldTranscriptionMode(str, Enum):
                        OPENAI_WHISPER = "openai_whisper"
                        LOCAL_WHISPER = "local_whisper"

                    return OldTranscriptionMode.LOCAL_WHISPER

            @property
            def model_name(self) -> str:
                if self._config.mode == TranscriptionMode.OPENAI:
                    return self._config.openai.whisper_model  # "whisper-1"
                else:
                    return self._config.local.whisper_model.value  # small/medium/large

            @property
            def api_key(self) -> Optional[str]:
                if self._config.mode == TranscriptionMode.OPENAI:
                    return self._config.openai.api_key
                else:
                    return None  # Local mode doesn't use OpenAI API key

            @property
            def enhanced_config(self) -> EnhancedTranscriptionConfig:
                # Update temperature from appropriate creativity setting based on mode
                if self._config.mode == TranscriptionMode.OPENAI:
                    self._enhanced_config._creativity = (
                        self._config.openai.gpt_creativity
                    )
                else:
                    self._enhanced_config._creativity = (
                        self._config.local.ollama_creativity
                    )
                return self._enhanced_config

        return TranscriptionConfigWrapper(self.transcription)

    @property
    def hotkey_config(self):
        """Backwards compatibility: Create wrapper with old hotkey structure."""

        class HotkeyConfigWrapper:
            def __init__(self, controls: ControlsConfig):
                self._controls = controls

            @property
            def key(self) -> str:
                return self._controls.basic_key

            @property
            def modifiers(self) -> List[str]:
                return []  # No modifiers in simplified config

            @property
            def description(self) -> str:
                return f"{self._controls.basic_key} key for basic transcription"

            @property
            def enhanced_key(self) -> str:
                return self._controls.enhanced_key

            @property
            def enhanced_modifiers(self) -> List[str]:
                return []  # No modifiers in simplified config

            @property
            def enhanced_description(self) -> str:
                return f"{self._controls.enhanced_key} key for enhanced transcription"

        return HotkeyConfigWrapper(self.controls)

    @property
    def auto_paste(self) -> bool:
        """Backwards compatibility: Use general.auto_paste instead."""
        return self.general.auto_paste

    @property
    def temp_directory(self) -> str:
        """Backwards compatibility: Return default temp directory."""
        from pathlib import Path

        return str(Path.home() / ".voicerecorder" / "temp")


# Backwards compatibility classes for existing code
class OpenAIConfig(BaseModel):
    """Backwards compatibility wrapper for old OpenAI config."""

    api_key: Optional[str] = Field(
        default=None, description="OpenAI API key for both Whisper and GPT"
    )


class EnhancedTranscriptionConfig(BaseModel):
    """Backwards compatibility wrapper for enhanced transcription config."""

    def __init__(self, **data):
        super().__init__(**data)
        self._creativity = 0.3

    @property
    def enabled(self) -> bool:
        """Always enabled - controlled by key press."""
        return True

    @property
    def provider(self):
        """Always OpenAI."""
        from enum import Enum

        class LLMProvider(str, Enum):
            OPENAI = "openai"

        return LLMProvider.OPENAI

    @property
    def model_name(self) -> str:
        """Hard-coded GPT model."""
        return "gpt-3.5-turbo"

    @property
    def api_key(self) -> Optional[str]:
        """Return None - API key is now in OpenAI config."""
        return None

    @property
    def prompt_template(self) -> str:
        """Hard-coded prompt template."""
        return "Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning:\n\n{transcript}"

    @property
    def max_tokens(self) -> int:
        """Hard-coded max tokens."""
        return 500

    @property
    def temperature(self) -> float:
        """Map to creativity setting."""
        return getattr(self, "_creativity", 0.3)

    @property
    def preserve_original(self) -> bool:
        """Always False - key choice determines output."""
        return False
