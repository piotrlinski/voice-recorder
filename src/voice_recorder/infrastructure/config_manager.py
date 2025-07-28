"""
Configuration manager for voice recorder application.
"""

import json
import os
from pathlib import Path
from typing import Optional

from ..domain.models import ApplicationConfig, AudioConfig, TranscriptionConfig, HotkeyConfig, TranscriptionMode, SoundConfig, SoundType


class ConfigManager:
    """Manages application configuration stored in user's home directory."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager."""
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to ~/.voicerecorder
            self.config_dir = Path.home() / ".voicerecorder"
        
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> ApplicationConfig:
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            # Create default configuration
            default_config = self._create_default_config()
            self.save_config(default_config)
            return default_config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return self._deserialize_config(config_data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading configuration: {e}")
            print("Creating default configuration...")
            default_config = self._create_default_config()
            self.save_config(default_config)
            return default_config

    def save_config(self, config: ApplicationConfig) -> None:
        """Save configuration to JSON file."""
        try:
            config_data = self._serialize_config(config)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to: {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def _create_default_config(self) -> ApplicationConfig:
        """Create default application configuration."""
        return ApplicationConfig(
            audio_config=AudioConfig(
                sample_rate=16000,
                channels=1,
                chunk_size=1024
            ),
            transcription_config=TranscriptionConfig(
                mode=TranscriptionMode.LOCAL_WHISPER,
                model_name="base",
                api_key=None,
                ollama_base_url="http://localhost:11434"
            ),
            hotkey_config=HotkeyConfig(
                key="shift",
                description="Shift key for recording"
            ),
            sound_config=SoundConfig(
                enabled=True,
                sound_type=SoundType.TONE,
                volume=0.15,
                start_frequency=800.0,
                end_frequency=1200.0,
                duration=0.3
            ),
            auto_paste=True,
            beep_feedback=True,
            temp_directory=str(Path.home() / ".voicerecorder" / "temp")
        )

    def _serialize_config(self, config: ApplicationConfig) -> dict:
        """Serialize ApplicationConfig to dictionary."""
        # Base transcription config
        transcription_config = {
            "mode": config.transcription_config.mode.value,
            "model_name": config.transcription_config.model_name,
        }
        
        # Add mode-specific fields
        if config.transcription_config.mode == TranscriptionMode.OPENAI_WHISPER:
            if config.transcription_config.api_key:
                transcription_config["api_key"] = config.transcription_config.api_key
        # Note: Ollama modes have been removed from the application
        
        return {
            "audio_config": {
                "sample_rate": config.audio_config.sample_rate,
                "channels": config.audio_config.channels,
                "format": config.audio_config.format.value,
                "chunk_size": config.audio_config.chunk_size
            },
            "transcription_config": transcription_config,
            "hotkey_config": {
                "key": config.hotkey_config.key,
                "modifiers": config.hotkey_config.modifiers,
                "description": config.hotkey_config.description
            },
            "sound_config": {
                "enabled": config.sound_config.enabled,
                "sound_type": config.sound_config.sound_type.value,
                "volume": config.sound_config.volume,
                "start_frequency": config.sound_config.start_frequency,
                "end_frequency": config.sound_config.end_frequency,
                "duration": config.sound_config.duration
            },
            "auto_paste": config.auto_paste,
            "beep_feedback": config.beep_feedback,
            "temp_directory": config.temp_directory
        }

    def _deserialize_config(self, config_data: dict) -> ApplicationConfig:
        """Deserialize dictionary to ApplicationConfig."""
        # Audio config
        audio_config = AudioConfig(
            sample_rate=config_data.get("audio_config", {}).get("sample_rate", 16000),
            channels=config_data.get("audio_config", {}).get("channels", 1),
            format=config_data.get("audio_config", {}).get("format", "wav"),
            chunk_size=config_data.get("audio_config", {}).get("chunk_size", 1024)
        )

        # Transcription config
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode(config_data.get("transcription_config", {}).get("mode", "local_whisper")),
            model_name=config_data.get("transcription_config", {}).get("model_name", "base"),
            api_key=config_data.get("transcription_config", {}).get("api_key"),
            ollama_base_url=config_data.get("transcription_config", {}).get("ollama_base_url", "http://localhost:11434")
        )

        # Hotkey config
        hotkey_config = HotkeyConfig(
            key=config_data.get("hotkey_config", {}).get("key", "shift"),
            modifiers=config_data.get("hotkey_config", {}).get("modifiers", []),
            description=config_data.get("hotkey_config", {}).get("description", "Shift key for recording")
        )

        # Sound config
        sound_config_data = config_data.get("sound_config", {})
        sound_config = SoundConfig(
            enabled=sound_config_data.get("enabled", True),
            sound_type=SoundType(sound_config_data.get("sound_type", "tone")),
            volume=sound_config_data.get("volume", 0.15),
            start_frequency=sound_config_data.get("start_frequency", 800.0),
            end_frequency=sound_config_data.get("end_frequency", 1200.0),
            duration=sound_config_data.get("duration", 0.3)
        )

        return ApplicationConfig(
            audio_config=audio_config,
            transcription_config=transcription_config,
            hotkey_config=hotkey_config,
            sound_config=sound_config,
            auto_paste=config_data.get("auto_paste", True),
            beep_feedback=config_data.get("beep_feedback", True),
            temp_directory=config_data.get("temp_directory", str(Path.home() / ".voicerecorder" / "temp"))
        )

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
            current_config.transcription_config.ollama_base_url = trans_data.get("ollama_base_url", current_config.transcription_config.ollama_base_url)

        # Update hotkey config
        if "hotkey_config" in kwargs:
            hotkey_data = kwargs["hotkey_config"]
            current_config.hotkey_config.key = hotkey_data.get("key", current_config.hotkey_config.key)
            current_config.hotkey_config.modifiers = hotkey_data.get("modifiers", current_config.hotkey_config.modifiers)
            current_config.hotkey_config.description = hotkey_data.get("description", current_config.hotkey_config.description)

        # Update other settings
        if "auto_paste" in kwargs:
            current_config.auto_paste = kwargs["auto_paste"]
        if "beep_feedback" in kwargs:
            current_config.beep_feedback = kwargs["beep_feedback"]
        if "temp_directory" in kwargs:
            current_config.temp_directory = kwargs["temp_directory"]

        self.save_config(current_config)
        return current_config

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
