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
    OLLAMA_WHISPER = "ollama_whisper"
    OLLAMA_MODEL = "ollama_model"


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
        description="Model name (OpenAI model or Ollama model)"
    )
    api_key: Optional[str] = Field(
        default=None, 
        description="API key for OpenAI (if using OpenAI mode)"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434", 
        description="Ollama server URL"
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
    auto_paste: bool = Field(default=True, description="Auto-paste transcribed text")
    beep_feedback: bool = Field(
        default=True, description="Audio feedback for recording"
    )
    temp_directory: str = Field(default="/tmp", description="Temporary file directory")
