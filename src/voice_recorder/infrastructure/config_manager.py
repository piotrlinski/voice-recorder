"""
INI-based configuration manager for voice recorder.
"""

import configparser
from pathlib import Path
from typing import Optional

from ..domain.models import (
    ApplicationConfig,
    AudioConfig,
    AudioFormat,
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
        has_nested_sections = config_parser.has_section(
            "transcription.openai"
        ) or config_parser.has_section("transcription.local")
        has_flat_sections = config_parser.has_section(
            "openai"
        ) or config_parser.has_section("controls")

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
            whisper_model=config_parser.get(
                "transcription.openai", "whisper_model", fallback="whisper-1"
            ),
            gpt_model=config_parser.get(
                "transcription.openai", "gpt_model", fallback="gpt-3.5-turbo"
            ),
            gpt_creativity=config_parser.getfloat(
                "transcription.openai", "gpt_creativity", fallback=0.3
            ),
        )

        # Load Local transcription config
        local_transcription_config = LocalTranscriptionConfig(
            whisper_model=LocalWhisperModel(
                config_parser.get(
                    "transcription.local", "whisper_model", fallback="small"
                )
            ),
            ollama_base_url=config_parser.get(
                "transcription.local",
                "ollama_base_url",
                fallback="http://localhost:11434",
            ),
            ollama_model=config_parser.get(
                "transcription.local", "ollama_model", fallback="llama3.1"
            ),
            ollama_creativity=config_parser.getfloat(
                "transcription.local", "ollama_creativity", fallback=0.3
            ),
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

        # General config
        general_config = GeneralConfig(
            auto_paste=config_parser.getboolean("general", "auto_paste", fallback=True)
        )

        return ApplicationConfig(
            transcription=transcription_config,
            controls=controls_config,
            audio=audio_config,
            general=general_config,
        )

    def _load_flat_format(
        self, config_parser: configparser.ConfigParser
    ) -> ApplicationConfig:
        """Load the flat configuration format (backwards compatibility)."""

        # Convert flat format to nested format by creating nested configs
        # Map "cloud" mode to "openai" mode for backwards compatibility
        mode_value = config_parser.get("transcription", "mode", fallback="cloud")
        transcription_mode = (
            TranscriptionMode.OPENAI
            if mode_value == "cloud"
            else TranscriptionMode.LOCAL
        )

        # Create OpenAI transcription config from flat format
        openai_transcription_config = OpenAITranscriptionConfig(
            api_key=config_parser.get("openai", "api_key", fallback=None),
            gpt_creativity=config_parser.getfloat(
                "transcription", "gpt_creativity", fallback=0.3
            ),
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

        # General config
        general_config = GeneralConfig(
            auto_paste=config_parser.getboolean("general", "auto_paste", fallback=True)
        )

        return ApplicationConfig(
            transcription=transcription_config,
            controls=controls_config,
            audio=audio_config,
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
            TranscriptionMode.OPENAI
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
        if "transcription_config" in kwargs:
            transcription_data = kwargs["transcription_config"]
            if "mode" in transcription_data:
                # Handle old mode values
                mode_value = transcription_data["mode"]
                if mode_value == "local_whisper":
                    current_config.transcription.mode = TranscriptionMode.LOCAL
                elif mode_value == "openai_whisper":
                    current_config.transcription.mode = TranscriptionMode.OPENAI
                else:
                    current_config.transcription.mode = TranscriptionMode(mode_value)

            if "model_name" in transcription_data:
                # Convert model_name to whisper_model for local config
                model_name = transcription_data["model_name"]
                if model_name == "base":
                    # base is not a valid enum value, use small instead
                    current_config.transcription.local.whisper_model = (
                        LocalWhisperModel.SMALL
                    )
                else:
                    try:
                        current_config.transcription.local.whisper_model = (
                            LocalWhisperModel(model_name)
                        )
                    except ValueError:
                        # Fall back to small if invalid
                        current_config.transcription.local.whisper_model = (
                            LocalWhisperModel.SMALL
                        )

        if "transcription_mode" in kwargs:
            current_config.transcription.mode = TranscriptionMode(
                kwargs["transcription_mode"]
            )
        if "local_model" in kwargs:
            current_config.transcription.local.whisper_model = LocalWhisperModel(
                kwargs["local_model"]
            )
        if "gpt_creativity" in kwargs:
            current_config.transcription.openai.gpt_creativity = kwargs[
                "gpt_creativity"
            ]

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

        # Update general config
        if "auto_paste" in kwargs:
            current_config.general.auto_paste = kwargs["auto_paste"]

        self.save_config(current_config)
        return current_config
