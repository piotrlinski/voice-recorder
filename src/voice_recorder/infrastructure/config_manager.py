"""
INI-based configuration manager for voice recorder.
"""

import configparser
import os
from pathlib import Path
from typing import Optional

from ..domain.models import (
    ApplicationConfig,
    AudioConfig,
    AudioFormat,
    HotkeyConfig,
    SoundConfig,
    SoundType,
    TranscriptionConfig,
    TranscriptionMode,
)


class ConfigManager:
    """Configuration manager using INI format."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize INI config manager."""
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".voicerecorder"
        
        self.config_file = self.config_dir / "config.ini"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> ApplicationConfig:
        """Load configuration from INI file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_file)

        # Audio config
        audio_config = AudioConfig(
            sample_rate=config_parser.getint("audio", "sample_rate", fallback=16000),
            channels=config_parser.getint("audio", "channels", fallback=1),
            format=AudioFormat(config_parser.get("audio", "format", fallback="wav")),
            chunk_size=config_parser.getint("audio", "chunk_size", fallback=1024)
        )

        # Transcription config
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode(config_parser.get("transcription", "mode", fallback="openai_whisper")),
            model_name=config_parser.get("transcription", "model_name", fallback="whisper-1"),
            api_key=config_parser.get("transcription", "api_key", fallback=None)
        )

        # Hotkey config
        hotkey_config = HotkeyConfig(
            key=config_parser.get("hotkey", "key", fallback="shift"),
            modifiers=config_parser.get("hotkey", "modifiers", fallback="").split(",") if config_parser.get("hotkey", "modifiers", fallback="") else [],
            description=config_parser.get("hotkey", "description", fallback="Shift key for recording")
        )

        # Sound config
        sound_config = SoundConfig(
            enabled=config_parser.getboolean("sound", "enabled", fallback=True),
            sound_type=SoundType(config_parser.get("sound", "sound_type", fallback="tone")),
            volume=config_parser.getfloat("sound", "volume", fallback=0.15),
            start_frequency=config_parser.getfloat("sound", "start_frequency", fallback=800.0),
            end_frequency=config_parser.getfloat("sound", "end_frequency", fallback=1200.0),
            duration=config_parser.getfloat("sound", "duration", fallback=0.3)
        )

        # General settings
        auto_paste = config_parser.getboolean("general", "auto_paste", fallback=True)
        temp_directory = config_parser.get("general", "temp_directory", fallback=str(Path.home() / ".voicerecorder" / "temp"))

        return ApplicationConfig(
            audio_config=audio_config,
            transcription_config=transcription_config,
            hotkey_config=hotkey_config,
            sound_config=sound_config,
            auto_paste=auto_paste,
            temp_directory=temp_directory
        )

    def save_config(self, config: ApplicationConfig) -> None:
        """Save configuration to INI file."""
        config_parser = configparser.ConfigParser()

        # Audio section
        config_parser["audio"] = {
            "sample_rate": str(config.audio_config.sample_rate),
            "channels": str(config.audio_config.channels),
            "format": config.audio_config.format.value,
            "chunk_size": str(config.audio_config.chunk_size)
        }

        # Transcription section
        transcription_section = {
            "mode": config.transcription_config.mode.value,
            "model_name": config.transcription_config.model_name,
        }
        if config.transcription_config.api_key:
            transcription_section["api_key"] = config.transcription_config.api_key
        config_parser["transcription"] = transcription_section

        # Hotkey section
        config_parser["hotkey"] = {
            "key": config.hotkey_config.key,
            "modifiers": ",".join(config.hotkey_config.modifiers),
            "description": config.hotkey_config.description
        }

        # Sound section
        config_parser["sound"] = {
            "enabled": str(config.sound_config.enabled),
            "sound_type": config.sound_config.sound_type.value,
            "volume": str(config.sound_config.volume),
            "start_frequency": str(config.sound_config.start_frequency),
            "end_frequency": str(config.sound_config.end_frequency),
            "duration": str(config.sound_config.duration)
        }

        # General section
        config_parser["general"] = {
            "auto_paste": str(config.auto_paste),
            "temp_directory": config.temp_directory
        }

        with open(self.config_file, "w") as f:
            config_parser.write(f)

    def config_exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_file.exists()

    def create_default_config(self) -> ApplicationConfig:
        """Create and save default configuration."""
        default_config = self._create_default_config()
        self.save_config(default_config)
        return default_config

    def _create_default_config(self) -> ApplicationConfig:
        """Create default configuration."""
        return ApplicationConfig()

    def get_config_path(self) -> str:
        """Get the path to the configuration file."""
        return str(self.config_file)

    def get_temp_directory(self) -> str:
        """Get the configured temporary directory."""
        config = self.load_config()
        temp_dir = Path(config.temp_directory)
        temp_dir.mkdir(parents=True, exist_ok=True)
        return str(temp_dir)

    def reset_to_defaults(self) -> ApplicationConfig:
        """Reset configuration to defaults."""
        default_config = self._create_default_config()
        self.save_config(default_config)
        return default_config

    def update_config(self, **kwargs) -> ApplicationConfig:
        """Update configuration with new values."""
        current_config = self.load_config()
        
        # Update audio config
        if "audio_config" in kwargs:
            audio_data = kwargs["audio_config"]
            current_config.audio_config.sample_rate = audio_data.get("sample_rate", current_config.audio_config.sample_rate)
            current_config.audio_config.channels = audio_data.get("channels", current_config.audio_config.channels)
            current_config.audio_config.format = audio_data.get("format", current_config.audio_config.format)
            current_config.audio_config.chunk_size = audio_data.get("chunk_size", current_config.audio_config.chunk_size)

        # Update transcription config
        if "transcription_config" in kwargs:
            trans_data = kwargs["transcription_config"]
            current_config.transcription_config.mode = TranscriptionMode(trans_data.get("mode", current_config.transcription_config.mode.value))
            current_config.transcription_config.model_name = trans_data.get("model_name", current_config.transcription_config.model_name)
            current_config.transcription_config.api_key = trans_data.get("api_key", current_config.transcription_config.api_key)


        # Update hotkey config
        if "hotkey_config" in kwargs:
            hotkey_data = kwargs["hotkey_config"]
            current_config.hotkey_config.key = hotkey_data.get("key", current_config.hotkey_config.key)
            current_config.hotkey_config.modifiers = hotkey_data.get("modifiers", current_config.hotkey_config.modifiers)
            current_config.hotkey_config.description = hotkey_data.get("description", current_config.hotkey_config.description)

        # Update sound config
        if "sound_config" in kwargs:
            sound_data = kwargs["sound_config"]
            current_config.sound_config.enabled = sound_data.get("sound_enabled", current_config.sound_config.enabled)
            current_config.sound_config.sound_type = SoundType(sound_data.get("sound_type", current_config.sound_config.sound_type.value))
            current_config.sound_config.volume = sound_data.get("sound_volume", current_config.sound_config.volume)
            current_config.sound_config.duration = sound_data.get("sound_duration", current_config.sound_config.duration)
            current_config.sound_config.start_frequency = sound_data.get("sound_start_frequency", current_config.sound_config.start_frequency)
            current_config.sound_config.end_frequency = sound_data.get("sound_end_frequency", current_config.sound_config.end_frequency)

        # Update other settings
        if "auto_paste" in kwargs:
            current_config.auto_paste = kwargs["auto_paste"]
        if "temp_directory" in kwargs:
            current_config.temp_directory = kwargs["temp_directory"]

        self.save_config(current_config)
        return current_config 