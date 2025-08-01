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
    SoundConfig,
    SoundType,
    TranscriptionConfig,
    TranscriptionMode,
    LocalWhisperModel,
    OpenAITranscriptionConfig,
    LocalTranscriptionConfig,
    ControlsConfig,
    GeneralConfig,
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
        """Load configuration from INI file (supports both old and new formats)."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_file)

        # Detect format by checking for nested sections
        has_nested_sections = (
            config_parser.has_section("transcription.openai") or 
            config_parser.has_section("transcription.local")
        )
        has_flat_sections = (
            config_parser.has_section("openai") or 
            config_parser.has_section("controls")
        )

        if has_nested_sections:
            return self._load_nested_format(config_parser)
        elif has_flat_sections:
            return self._load_flat_format(config_parser)
        else:
            return self._load_old_format(config_parser)

    def _load_nested_format(
        self, config_parser: configparser.ConfigParser
    ) -> ApplicationConfig:
        """Load the new nested configuration format."""
        
        # Load transcription mode
        transcription_mode = TranscriptionMode(
            config_parser.get("transcription", "mode", fallback="openai")
        )

        # Load OpenAI transcription config
        openai_transcription_config = OpenAITranscriptionConfig(
            api_key=config_parser.get("transcription.openai", "api_key", fallback=None),
            whisper_model=config_parser.get("transcription.openai", "whisper_model", fallback="whisper-1"),
            gpt_model=config_parser.get("transcription.openai", "gpt_model", fallback="gpt-3.5-turbo"),
            gpt_creativity=config_parser.getfloat("transcription.openai", "gpt_creativity", fallback=0.3),
        )

        # Load Local transcription config
        local_transcription_config = LocalTranscriptionConfig(
            whisper_model=LocalWhisperModel(
                config_parser.get("transcription.local", "whisper_model", fallback="small")
            ),
            ollama_base_url=config_parser.get("transcription.local", "ollama_base_url", fallback="http://localhost:11434"),
            ollama_model=config_parser.get("transcription.local", "ollama_model", fallback="llama3.1"),
            ollama_creativity=config_parser.getfloat("transcription.local", "ollama_creativity", fallback=0.3),
        )

        # Transcription config
        transcription_config = TranscriptionConfig(
            mode=transcription_mode,
            openai=openai_transcription_config,
            local=local_transcription_config,
        )

        # Controls config
        controls_config = ControlsConfig(
            basic_key=config_parser.get("controls", "basic_key", fallback="shift_r"),
            enhanced_key=config_parser.get("controls", "enhanced_key", fallback="ctrl_l"),
        )

        # Audio config
        audio_config = AudioConfig(
            sample_rate=config_parser.getint("audio", "sample_rate", fallback=16000),
            channels=config_parser.getint("audio", "channels", fallback=1),
            format=AudioFormat(config_parser.get("audio", "format", fallback="wav")),
            chunk_size=config_parser.getint("audio", "chunk_size", fallback=1024),
        )

        # Sound config
        sound_config = SoundConfig(
            enabled=config_parser.getboolean("sound", "enabled", fallback=True),
            volume=config_parser.getint("sound", "volume", fallback=15),
            basic_sound_type=SoundType(
                config_parser.get("sound", "basic_sound_type", fallback="tone")
            ),
            basic_start_frequency=config_parser.getfloat(
                "sound", "basic_start_frequency", fallback=800.0
            ),
            basic_end_frequency=config_parser.getfloat(
                "sound", "basic_end_frequency", fallback=1200.0
            ),
            enhanced_sound_type=SoundType(
                config_parser.get("sound", "enhanced_sound_type", fallback="tone")
            ),
            enhanced_start_frequency=config_parser.getfloat(
                "sound", "enhanced_start_frequency", fallback=1000.0
            ),
            enhanced_end_frequency=config_parser.getfloat(
                "sound", "enhanced_end_frequency", fallback=1400.0
            ),
            duration=config_parser.getfloat("sound", "duration", fallback=0.3),
        )

        # General config
        general_config = GeneralConfig(
            auto_paste=config_parser.getboolean("general", "auto_paste", fallback=True)
        )

        return ApplicationConfig(
            transcription=transcription_config,
            controls=controls_config,
            audio=audio_config,
            sound=sound_config,
            general=general_config,
        )

    def _load_flat_format(
        self, config_parser: configparser.ConfigParser
    ) -> ApplicationConfig:
        """Load the flat configuration format (backwards compatibility)."""

        # Convert flat format to nested format by creating nested configs
        # Map "cloud" mode to "openai" mode for backwards compatibility
        mode_value = config_parser.get("transcription", "mode", fallback="cloud")
        transcription_mode = TranscriptionMode.OPENAI if mode_value == "cloud" else TranscriptionMode.LOCAL

        # Create OpenAI transcription config from flat format
        openai_transcription_config = OpenAITranscriptionConfig(
            api_key=config_parser.get("openai", "api_key", fallback=None),
            gpt_creativity=config_parser.getfloat("transcription", "gpt_creativity", fallback=0.3),
        )

        # Create Local transcription config from flat format
        local_transcription_config = LocalTranscriptionConfig(
            whisper_model=LocalWhisperModel(
                config_parser.get("transcription", "local_model", fallback="small")
            ),
        )

        # Transcription config with nested structure
        transcription_config = TranscriptionConfig(
            mode=transcription_mode,
            openai=openai_transcription_config,
            local=local_transcription_config,
        )

        # Controls config
        controls_config = ControlsConfig(
            basic_key=config_parser.get("controls", "basic_key", fallback="shift_r"),
            enhanced_key=config_parser.get(
                "controls", "enhanced_key", fallback="ctrl_l"
            ),
        )

        # Audio config
        audio_config = AudioConfig(
            sample_rate=config_parser.getint("audio", "sample_rate", fallback=16000),
            channels=config_parser.getint("audio", "channels", fallback=1),
            format=AudioFormat(config_parser.get("audio", "format", fallback="wav")),
            chunk_size=config_parser.getint("audio", "chunk_size", fallback=1024),
        )

        # Sound config
        sound_config = SoundConfig(
            enabled=config_parser.getboolean("sound", "enabled", fallback=True),
            volume=config_parser.getint("sound", "volume", fallback=15),
            basic_sound_type=SoundType(
                config_parser.get("sound", "basic_sound_type", fallback="tone")
            ),
            basic_start_frequency=config_parser.getfloat(
                "sound", "basic_start_frequency", fallback=800.0
            ),
            basic_end_frequency=config_parser.getfloat(
                "sound", "basic_end_frequency", fallback=1200.0
            ),
            enhanced_sound_type=SoundType(
                config_parser.get("sound", "enhanced_sound_type", fallback="tone")
            ),
            enhanced_start_frequency=config_parser.getfloat(
                "sound", "enhanced_start_frequency", fallback=1000.0
            ),
            enhanced_end_frequency=config_parser.getfloat(
                "sound", "enhanced_end_frequency", fallback=1400.0
            ),
            duration=config_parser.getfloat("sound", "duration", fallback=0.3),
        )

        # General config
        general_config = GeneralConfig(
            auto_paste=config_parser.getboolean("general", "auto_paste", fallback=True)
        )

        return ApplicationConfig(
            transcription=transcription_config,
            controls=controls_config,
            audio=audio_config,
            sound=sound_config,
            general=general_config,
        )

    def _load_old_format(
        self, config_parser: configparser.ConfigParser
    ) -> ApplicationConfig:
        """Load and migrate from old configuration format."""
        # Extract OpenAI API key from old locations
        api_key = config_parser.get(
            "transcription", "openai_api_key", fallback=None
        ) or config_parser.get("enhanced_transcription", "api_key", fallback=None)

        # Map old transcription mode to new mode
        old_mode = config_parser.get("transcription", "mode", fallback="openai_whisper")
        new_mode = (
            TranscriptionMode.CLOUD
            if old_mode == "openai_whisper"
            else TranscriptionMode.LOCAL
        )

        # Extract local model name (or use default)
        model_name = config_parser.get(
            "transcription", "model_name", fallback="whisper-1"
        )
        local_model = LocalWhisperModel.SMALL  # Default
        if model_name in ["small", "medium", "large"]:
            local_model = LocalWhisperModel(model_name)

        # Extract creativity from old temperature setting
        creativity = config_parser.getfloat(
            "enhanced_transcription", "temperature", fallback=0.3
        )

        # Extract hotkeys from old format
        basic_key = config_parser.get("hotkey", "key", fallback="shift_r")
        enhanced_key = config_parser.get("hotkey", "enhanced_key", fallback="ctrl_l")

        # Convert old volume format (0.0-1.0) to new format (0-100)
        old_volume = config_parser.getfloat("sound", "volume", fallback=0.15)
        new_volume = int(old_volume * 100) if old_volume <= 1.0 else int(old_volume)

        # Create new format config from old values
        from ..domain.models import OpenAIConfig, ControlsConfig, GeneralConfig

        return ApplicationConfig(
            openai=OpenAIConfig(api_key=api_key),
            transcription=TranscriptionConfig(
                mode=new_mode, local_model=local_model, gpt_creativity=creativity
            ),
            controls=ControlsConfig(basic_key=basic_key, enhanced_key=enhanced_key),
            audio=AudioConfig(
                sample_rate=config_parser.getint(
                    "audio", "sample_rate", fallback=16000
                ),
                channels=config_parser.getint("audio", "channels", fallback=1),
                format=AudioFormat(
                    config_parser.get("audio", "format", fallback="wav")
                ),
                chunk_size=config_parser.getint("audio", "chunk_size", fallback=1024),
            ),
            sound=SoundConfig(
                enabled=config_parser.getboolean("sound", "enabled", fallback=True),
                volume=new_volume,
                basic_sound_type=SoundType(
                    config_parser.get("sound", "sound_type", fallback="tone")
                ),
                basic_start_frequency=config_parser.getfloat(
                    "sound", "start_frequency", fallback=800.0
                ),
                basic_end_frequency=config_parser.getfloat(
                    "sound", "end_frequency", fallback=1200.0
                ),
                enhanced_sound_type=SoundType.TONE,  # Default for enhanced
                enhanced_start_frequency=1000.0,
                enhanced_end_frequency=1400.0,
                duration=config_parser.getfloat("sound", "duration", fallback=0.3),
            ),
            general=GeneralConfig(
                auto_paste=config_parser.getboolean(
                    "general", "auto_paste", fallback=True
                )
            ),
        )

    def save_config(self, config: ApplicationConfig) -> None:
        """Save configuration to new nested INI format."""
        config_parser = configparser.ConfigParser()

        # Transcription main section
        config_parser["transcription"] = {
            "mode": config.transcription.mode.value,
        }

        # Nested OpenAI transcription section
        openai_section = {
            "whisper_model": config.transcription.openai.whisper_model,
            "gpt_model": config.transcription.openai.gpt_model,
            "gpt_creativity": str(config.transcription.openai.gpt_creativity),
        }
        if config.transcription.openai.api_key:
            openai_section["api_key"] = config.transcription.openai.api_key
        config_parser["transcription.openai"] = openai_section

        # Nested Local transcription section
        config_parser["transcription.local"] = {
            "whisper_model": config.transcription.local.whisper_model.value,
            "ollama_base_url": config.transcription.local.ollama_base_url,
            "ollama_model": config.transcription.local.ollama_model,
            "ollama_creativity": str(config.transcription.local.ollama_creativity),
        }

        # Controls section
        config_parser["controls"] = {
            "basic_key": config.controls.basic_key,
            "enhanced_key": config.controls.enhanced_key,
        }

        # Audio section
        config_parser["audio"] = {
            "sample_rate": str(config.audio.sample_rate),
            "channels": str(config.audio.channels),
            "format": config.audio.format.value,
            "chunk_size": str(config.audio.chunk_size),
        }

        # Sound section
        config_parser["sound"] = {
            "enabled": str(config.sound.enabled),
            "volume": str(config.sound.volume),
            "basic_sound_type": config.sound.basic_sound_type.value,
            "basic_start_frequency": str(config.sound.basic_start_frequency),
            "basic_end_frequency": str(config.sound.basic_end_frequency),
            "enhanced_sound_type": config.sound.enhanced_sound_type.value,
            "enhanced_start_frequency": str(config.sound.enhanced_start_frequency),
            "enhanced_end_frequency": str(config.sound.enhanced_end_frequency),
            "duration": str(config.sound.duration),
        }

        # General section
        config_parser["general"] = {"auto_paste": str(config.general.auto_paste)}

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
        """Get the default temporary directory."""
        temp_dir = Path.home() / ".voicerecorder" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return str(temp_dir)

    def reset_to_defaults(self) -> ApplicationConfig:
        """Reset configuration to defaults."""
        default_config = self._create_default_config()
        self.save_config(default_config)
        return default_config

    def update_config(self, **kwargs) -> ApplicationConfig:
        """Update configuration with new values (supports both old and new parameter names)."""
        current_config = self.load_config()

        # Update OpenAI config
        if "openai_api_key" in kwargs:
            current_config.openai.api_key = kwargs["openai_api_key"]

        # Update transcription config
        if "transcription_mode" in kwargs:
            current_config.transcription.mode = TranscriptionMode(
                kwargs["transcription_mode"]
            )
        if "local_model" in kwargs:
            current_config.transcription.local_model = LocalWhisperModel(
                kwargs["local_model"]
            )
        if "gpt_creativity" in kwargs:
            current_config.transcription.gpt_creativity = kwargs["gpt_creativity"]

        # Update controls config
        if "basic_key" in kwargs:
            current_config.controls.basic_key = kwargs["basic_key"]
        if "enhanced_key" in kwargs:
            current_config.controls.enhanced_key = kwargs["enhanced_key"]

        # Update audio config (backwards compatibility)
        if "audio_config" in kwargs:
            audio_data = kwargs["audio_config"]
            current_config.audio.sample_rate = audio_data.get(
                "sample_rate", current_config.audio.sample_rate
            )
            current_config.audio.channels = audio_data.get(
                "channels", current_config.audio.channels
            )
            current_config.audio.format = audio_data.get(
                "format", current_config.audio.format
            )
            current_config.audio.chunk_size = audio_data.get(
                "chunk_size", current_config.audio.chunk_size
            )

        # Update sound config (backwards compatibility)
        if "sound_config" in kwargs:
            sound_data = kwargs["sound_config"]
            current_config.sound.enabled = sound_data.get(
                "sound_enabled", current_config.sound.enabled
            )
            # Convert volume if needed
            volume = sound_data.get("sound_volume", current_config.sound.volume)
            if isinstance(volume, float) and volume <= 1.0:
                volume = int(volume * 100)
            current_config.sound.volume = volume

        # Update general config
        if "auto_paste" in kwargs:
            current_config.general.auto_paste = kwargs["auto_paste"]

        self.save_config(current_config)
        return current_config
