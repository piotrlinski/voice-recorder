"""
Interactive configuration wizard for Voice Recorder CLI.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

from ..domain.models import (
    ApplicationConfig,
    AudioConfig,
    AudioFormat,
    HotkeyConfig,
    SoundConfig,
    SoundType,
    TranscriptionConfig,
    TranscriptionMode,
    ControlsConfig,
    GeneralConfig,
)
from ..infrastructure.config_manager import ConfigManager
from ..infrastructure.logging_adapter import LoggingAdapter


class ConfigurationWizard:
    """Interactive configuration wizard for initial setup"""

    def __init__(self):
        self.console = LoggingAdapter()
        self.config_manager = ConfigManager()

    def run_wizard(self) -> ApplicationConfig:
        """Run the interactive configuration wizard"""
        self._print_welcome()

        # Check if config already exists
        if self.config_manager.config_exists():
            if not self._confirm_overwrite():
                self.console.info("Configuration wizard cancelled.")
                sys.exit(0)

        # Collect configuration
        transcription_config = self._configure_transcription()
        controls_config = self._configure_controls()
        sound_config = self._configure_sound()
        audio_config = self._configure_audio()
        general_config = self._configure_general()

        # Create final configuration
        config = ApplicationConfig(
            transcription=transcription_config,
            controls=controls_config,
            sound=sound_config,
            audio=audio_config,
            general=general_config,
        )

        # Save configuration
        self.config_manager.save_config(config)

        self._print_completion(config)
        return config

    def _print_welcome(self):
        """Print welcome message"""
        print("=" * 60)
        print("🎤 VOICE RECORDER - CONFIGURATION WIZARD")
        print("=" * 60)
        print()
        print("Welcome to Voice Recorder! This wizard will help you set up")
        print("your initial configuration for the best recording experience.")
        print()
        print("You can always change these settings later by editing:")
        print(f"📁 {self.config_manager.get_config_path()}")
        print()

    def _confirm_overwrite(self) -> bool:
        """Ask user if they want to overwrite existing config"""
        print("⚠️  Configuration file already exists!")
        print(f"📁 {self.config_manager.get_config_path()}")
        print()
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        return response in ["y", "yes"]

    def _configure_transcription(self) -> TranscriptionConfig:
        """Configure transcription settings"""
        print("🗣️  TRANSCRIPTION SETTINGS")
        print("-" * 40)
        print()
        print("Choose your transcription service:")
        print("1. OpenAI Whisper (Cloud) - High accuracy, requires API key")
        print("2. Local Whisper (Offline) - Works offline, uses your CPU")
        print()

        while True:
            choice = input("Select option (1 or 2): ").strip()
            if choice == "1":
                mode = TranscriptionMode.OPENAI
                api_key = self._get_openai_api_key()
                enhanced_prompt = self._get_enhanced_transcription_prompt()
                return TranscriptionConfig(
                    mode=mode,
                    openai=TranscriptionConfig.openai.model_validate({
                        "api_key": api_key,
                        "enhanced_transcription_prompt": enhanced_prompt
                    })
                )
            elif choice == "2":
                mode = TranscriptionMode.LOCAL
                local_model = self._get_local_whisper_model()
                enhanced_prompt = self._get_enhanced_transcription_prompt()
                return TranscriptionConfig(
                    mode=mode,
                    local=TranscriptionConfig.local.model_validate({
                        "whisper_model": local_model,
                        "enhanced_transcription_prompt": enhanced_prompt
                    })
                )
            else:
                print("❌ Please enter 1 or 2")

    def _get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from user"""
        print()
        print("🔑 OpenAI API Key Setup")
        print(
            "Enter your OpenAI API key - this will be stored securely in your configuration file."
        )
        print()

        api_key = input(
            "Enter OpenAI API key (required for OpenAI Whisper mode): "
        ).strip()
        if api_key:
            print("✅ API key saved securely in configuration")
        else:
            print(
                "⚠️  No API key provided - you'll need to edit the config file to add it later"
            )

        return api_key if api_key else None

    def _get_local_whisper_model(self) -> str:
        """Get local Whisper model selection"""
        print()
        print("📦 Local Whisper Model Selection")
        print("Available models (smaller = faster, larger = more accurate):")
        models = ["small", "medium", "large"]
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
        print()

        while True:
            choice = input("Select model (1-3): ").strip()
            if choice in ["1", "2", "3"]:
                model = models[int(choice) - 1]
                print(f"✅ Selected model: {model}")
                return model
            else:
                print("❌ Please enter 1, 2, or 3")

    def _configure_controls(self) -> ControlsConfig:
        """Configure hotkey settings"""
        print("⌨️  HOTKEY SETTINGS")
        print("-" * 40)
        print()
        print("Choose your recording hotkeys:")
        print("1. Right Shift (Basic) + Left Ctrl (Enhanced) - Recommended")
        print("2. Left Shift (Basic) + Right Ctrl (Enhanced)")
        print("3. Space (Basic) + Enter (Enhanced)")
        print("4. Custom keys")
        print()

        hotkey_options = {
            "1": ("shift_r", "ctrl_l", "Right Shift + Left Ctrl"),
            "2": ("shift_l", "ctrl_r", "Left Shift + Right Ctrl"),
            "3": ("space", "enter", "Space + Enter"),
        }

        while True:
            choice = input("Select option (1-4): ").strip()
            if choice in hotkey_options:
                basic_key, enhanced_key, description = hotkey_options[choice]
                break
            elif choice == "4":
                basic_key, enhanced_key, description = self._get_custom_hotkeys()
                break
            else:
                print("❌ Please enter 1, 2, 3, or 4")

        print(f"✅ Hotkeys: {description}")
        print()

        return ControlsConfig(basic_key=basic_key, enhanced_key=enhanced_key)

    def _get_custom_hotkeys(self) -> tuple[str, str, str]:
        """Get custom hotkeys from user"""
        print()
        print("🎯 Custom Hotkey Setup")
        print("Enter the keys you want to use (e.g., 'f1', 'ctrl', 'alt', etc.)")
        print("Common keys: f1-f12, ctrl, alt, shift, space, tab, enter")
        print()

        basic_key = input("Enter basic transcription key: ").strip().lower()
        if not basic_key:
            basic_key = "shift_r"

        enhanced_key = input("Enter enhanced transcription key: ").strip().lower()
        if not enhanced_key:
            enhanced_key = "ctrl_l"

        description = f"{basic_key} + {enhanced_key}"

        return basic_key, enhanced_key, description

    def _configure_sound(self) -> SoundConfig:
        """Configure sound feedback settings"""
        print("🔊 SOUND FEEDBACK SETTINGS")
        print("-" * 40)
        print()

        # Enable/disable sound
        enable_sound = self._get_yes_no(
            "Enable sound feedback for recording? (Y/n): ", True
        )

        if not enable_sound:
            print("✅ Sound feedback disabled")
            print()
            return SoundConfig(enabled=False)

        # Disable start sounds option
        print()
        disable_start_sounds = self._get_yes_no(
            "Disable start recording sounds (keep stop sounds)? (y/N): ", False
        )

        # Volume
        print()
        volume = self._get_int_input(
            "Sound volume (0-100, default: 15): ",
            default=15,
            min_val=0,
            max_val=100,
        )

        # Sound type for basic transcription
        print()
        print("Choose sound type for basic transcription:")
        print("1. Tone (Recommended) - Pleasant sweep tones")
        print("2. Beep - Simple system beep")
        print("3. None - No sound")
        print()

        while True:
            choice = input("Select basic sound type (1, 2, or 3): ").strip()
            if choice == "1":
                basic_sound_type = SoundType.TONE
                break
            elif choice == "2":
                basic_sound_type = SoundType.BEEP
                break
            elif choice == "3":
                basic_sound_type = SoundType.NONE
                break
            else:
                print("❌ Please enter 1, 2, or 3")

        # Sound type for enhanced transcription
        print()
        print("Choose sound type for enhanced transcription:")
        print("1. Tone (Recommended) - Pleasant sweep tones")
        print("2. Beep - Simple system beep")
        print("3. None - No sound")
        print()

        while True:
            choice = input("Select enhanced sound type (1, 2, or 3): ").strip()
            if choice == "1":
                enhanced_sound_type = SoundType.TONE
                break
            elif choice == "2":
                enhanced_sound_type = SoundType.BEEP
                break
            elif choice == "3":
                enhanced_sound_type = SoundType.NONE
                break
            else:
                print("❌ Please enter 1, 2, or 3")

        # Duration
        print()
        duration = self._get_float_input(
            "Sound duration in seconds (0.1-1.0, default: 0.3): ",
            default=0.3,
            min_val=0.1,
            max_val=1.0,
        )

        print(f"✅ Sound: Basic={basic_sound_type.value}, Enhanced={enhanced_sound_type.value}")
        print(f"   Volume: {volume}%, Duration: {duration}s")
        if disable_start_sounds:
            print("   Start sounds: Disabled (stop sounds only)")
        print()

        return SoundConfig(
            enabled=True,
            disable_start_sounds=disable_start_sounds,
            volume=volume,
            basic_sound_type=basic_sound_type,
            basic_start_frequency=600.0,
            basic_end_frequency=800.0,
            enhanced_sound_type=enhanced_sound_type,
            enhanced_start_frequency=1000.0,
            enhanced_end_frequency=1200.0,
            duration=duration,
        )

    def _configure_audio(self) -> AudioConfig:
        """Configure audio recording settings"""
        print("🎙️  AUDIO RECORDING SETTINGS")
        print("-" * 40)
        print()

        # Most users can use defaults, but offer customization
        use_defaults = self._get_yes_no("Use recommended audio settings? (Y/n): ", True)

        if use_defaults:
            print("✅ Using recommended audio settings:")
            print("   • Sample Rate: 16000 Hz")
            print("   • Channels: 1 (Mono)")
            print("   • Format: WAV")
            print("   • Chunk Size: 1024")
            print()
            return AudioConfig()

        # Custom audio settings
        print()
        print("📊 Custom Audio Settings")

        sample_rate = self._get_int_input(
            "Sample rate (8000, 16000, 44100, default: 16000): ",
            default=16000,
            valid_values=[8000, 16000, 22050, 44100, 48000],
        )

        channels = self._get_int_input(
            "Channels (1=mono, 2=stereo, default: 1): ", default=1, min_val=1, max_val=2
        )

        print(f"✅ Audio: {sample_rate}Hz, {channels} channel(s)")
        print()

        return AudioConfig(
            sample_rate=sample_rate,
            channels=channels,
            format=AudioFormat.WAV,
            chunk_size=1024,
        )

    def _configure_general(self) -> GeneralConfig:
        """Configure general application settings"""
        print("⚙️  GENERAL SETTINGS")
        print("-" * 40)
        print()

        # Auto-paste setting
        auto_paste = self._get_yes_no(
            "Auto-paste transcribed text at cursor position? (Y/n): ", True
        )

        print(f"✅ Auto-paste: {'Enabled' if auto_paste else 'Disabled'}")
        print()

        return GeneralConfig(auto_paste=auto_paste)

    def _print_completion(self, config: ApplicationConfig):
        """Print configuration completion message"""
        print("=" * 60)
        print("🎉 CONFIGURATION COMPLETE!")
        print("=" * 60)
        print()
        print("Your Voice Recorder is now configured and ready to use!")
        print()
        print("📋 Configuration Summary:")
        print(f"   🗣️  Transcription: {config.transcription.mode.value}")
        print(f"   ⌨️  Basic Key: {config.controls.basic_key}")
        print(f"   ⌨️  Enhanced Key: {config.controls.enhanced_key}")
        print(
            f"   🔊 Sound: {'Enabled' if config.sound.enabled else 'Disabled'}"
        )
        print(f"   📋 Auto-paste: {'Enabled' if config.general.auto_paste else 'Disabled'}")
        print()
        print("📁 Configuration saved to:")
        print(f"   {self.config_manager.get_config_path()}")
        print()
        print("🚀 To start recording, run:")
        print("   voice-recorder")
        print()
        print("🖥️  For GUI interface, run:")
        print("   voice-recorder-gui")
        print()

    # Helper methods
    def _get_yes_no(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no input from user"""
        while True:
            response = input(prompt).strip().lower()
            if not response:
                return default
            if response in ["y", "yes", "true", "1"]:
                return True
            elif response in ["n", "no", "false", "0"]:
                return False
            else:
                print("❌ Please enter y/yes or n/no")

    def _get_int_input(
        self,
        prompt: str,
        default: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        valid_values: Optional[List[int]] = None,
    ) -> int:
        """Get integer input from user with validation"""
        while True:
            response = input(prompt).strip()
            if not response:
                return default

            try:
                value = int(response)

                if valid_values and value not in valid_values:
                    print(f"❌ Please enter one of: {valid_values}")
                    continue

                if min_val is not None and value < min_val:
                    print(f"❌ Value must be at least {min_val}")
                    continue

                if max_val is not None and value > max_val:
                    print(f"❌ Value must be at most {max_val}")
                    continue

                return value

            except ValueError:
                print("❌ Please enter a valid number")

    def _get_float_input(
        self,
        prompt: str,
        default: float,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> float:
        """Get float input from user with validation"""
        while True:
            response = input(prompt).strip()
            if not response:
                return default

            try:
                value = float(response)

                if min_val is not None and value < min_val:
                    print(f"❌ Value must be at least {min_val}")
                    continue

                if max_val is not None and value > max_val:
                    print(f"❌ Value must be at most {max_val}")
                    continue

                return value

            except ValueError:
                print("❌ Please enter a valid number")

    def _get_enhanced_transcription_prompt(self) -> str:
        """Get enhanced transcription prompt from user"""
        print()
        print("🤖 ENHANCED TRANSCRIPTION PROMPT")
        print("-" * 40)
        print("This prompt will be used to enhance your transcribed text with AI.")
        print("You can customize how the AI improves your text.")
        print()
        
        use_default = self._get_yes_no(
            "Use default enhancement prompt? (Y/n): ", True
        )
        
        if use_default:
            default_prompt = "Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary."
            print("✅ Using default enhancement prompt")
            return default_prompt
        
        print()
        print("📝 Custom Enhancement Prompt")
        print("Enter your custom prompt for text enhancement:")
        print("(The transcribed text will be appended to this prompt)")
        print()
        
        custom_prompt = input("Enter custom prompt: ").strip()
        if not custom_prompt:
            print("⚠️  No prompt provided, using default")
            return "Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary."
        
        print("✅ Custom enhancement prompt saved")
        return custom_prompt
