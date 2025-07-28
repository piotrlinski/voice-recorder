"""
Domain models for the voice recorder application.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RecordingState(str, Enum):
    """Recording state enumeration."""

    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    ERROR = "error"


class AudioFormat(str, Enum):
    """Audio format enumeration."""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"


class TranscriptionMode(str, Enum):
    """Transcription mode enumeration."""

    OPENAI_WHISPER = "openai_whisper"
    LOCAL_WHISPER = "local_whisper"


class SoundType(str, Enum):
    """Sound type enumeration."""

    TONE = "tone"
    BEEP = "beep"
    NONE = "none"


class AudioConfig(BaseModel):
    """Audio recording configuration."""

    sample_rate: int = Field(default=16000, description="Sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    format: AudioFormat = Field(default=AudioFormat.WAV, description="Audio format")
    chunk_size: int = Field(default=1024, description="Audio chunk size")


class TranscriptionConfig(BaseModel):
    """Transcription configuration."""

    mode: TranscriptionMode = Field(
        default=TranscriptionMode.OPENAI_WHISPER, 
        description="Transcription mode"
    )
    model_name: str = Field(
        default="whisper-1", 
        description="Model name (OpenAI model or local Whisper model)"
    )
    api_key: Optional[str] = Field(
        default=None, 
        description="API key for OpenAI (if using OpenAI mode)"
    )


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


class SoundConfig(BaseModel):
    """Sound feedback configuration."""

    enabled: bool = Field(default=True, description="Enable audio feedback")
    sound_type: SoundType = Field(default=SoundType.TONE, description="Type of sound to play")
    volume: float = Field(default=0.15, ge=0.0, le=1.0, description="Sound volume (0.0 to 1.0)")
    start_frequency: float = Field(default=800.0, description="Start frequency for tone (Hz)")
    end_frequency: float = Field(default=1200.0, description="End frequency for tone (Hz)")
    duration: float = Field(default=0.3, description="Sound duration in seconds")


class HotkeyConfig(BaseModel):
    """Hotkey configuration."""

    key: str = Field(description="Key to trigger recording")
    modifiers: List[str] = Field(default_factory=list, description="Modifier keys")
    description: str = Field(description="Human-readable description")


class ApplicationConfig(BaseModel):
    """Application configuration."""

    audio_config: AudioConfig = Field(default_factory=AudioConfig)
    transcription_config: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    hotkey_config: HotkeyConfig = Field(
        default=HotkeyConfig(key="shift", description="Shift key for recording")
    )
    sound_config: SoundConfig = Field(default_factory=SoundConfig)
    auto_paste: bool = Field(default=True, description="Auto-paste transcribed text")
    beep_feedback: bool = Field(
        default=True, description="Audio feedback for recording (deprecated, use sound_config)"
    )
    temp_directory: str = Field(default="/tmp", description="Temporary file directory")
