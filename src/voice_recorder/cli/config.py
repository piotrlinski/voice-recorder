"""
Configuration CLI module for voice recorder.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..domain.models import TranscriptionMode
from ..infrastructure.config_manager import ConfigManager

console = Console()


def get_user_choice(prompt: str, options: list) -> int:
    """Get user choice from a list of options."""
    console.print(f"\n{prompt}")
    for i, option in enumerate(options):
        console.print(f"  {i + 1}. {option}")
    
    while True:
        try:
            choice = int(input(f"\nEnter choice (1-{len(options)}): ")) - 1
            if 0 <= choice < len(options):
                return choice
            else:
                console.print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            console.print("Please enter a valid number")


def configure_transcription_mode() -> dict:
    """Configure transcription mode."""
    console.print("\n🤖 Transcription Mode Configuration")
    console.print("=" * 40)
    
    modes = [
        ("local_whisper", "Local Whisper (offline, requires model download)"),
        ("openai_whisper", "OpenAI Whisper (cloud-based, requires API key)")
    ]
    
    console.print("\nAvailable transcription modes:")
    for i, (mode, description) in enumerate(modes):
        console.print(f"  {i + 1}. {description}")
    
    choice = get_user_choice("Select transcription mode:", [desc for _, desc in modes])
    selected_mode = modes[choice][0]
    
    config = {"mode": selected_mode}
    
    if selected_mode == "local_whisper":
        console.print("\n📋 Available Whisper Models:")
        models = [
            ("tiny", "39 MB (fastest, least accurate)"),
            ("base", "74 MB (good balance)"),
            ("small", "244 MB (more accurate)"),
            ("medium", "769 MB (very accurate)"),
            ("large", "1550 MB (most accurate, slowest)")
        ]
        
        for i, (model, desc) in enumerate(models):
            console.print(f"  {i + 1}. {model} - {desc}")
        
        model_choice = get_user_choice("Select model:", [desc for _, desc in models])
        config["model_name"] = models[model_choice][0]
        
    elif selected_mode == "openai_whisper":
        config["model_name"] = "whisper-1"
        api_key = input("\nEnter OpenAI API key (or press Enter to use environment variable): ").strip()
        if api_key:
            config["api_key"] = api_key
        else:
            config["api_key"] = None
            
    # Note: Ollama modes have been removed from the application
    
    return config


def configure_audio_settings() -> dict:
    """Configure audio settings."""
    console.print("\n🔊 Audio Configuration")
    console.print("=" * 30)
    
    sample_rate = input("Sample rate in Hz (default: 16000): ").strip()
    sample_rate = int(sample_rate) if sample_rate else 16000
    
    channels = input("Number of channels (1=mono, 2=stereo, default: 1): ").strip()
    channels = int(channels) if channels else 1
    
    chunk_size = input("Audio chunk size (default: 1024): ").strip()
    chunk_size = int(chunk_size) if chunk_size else 1024
    
    return {
        "sample_rate": sample_rate,
        "channels": channels,
        "chunk_size": chunk_size
    }


def configure_hotkey_settings() -> dict:
    """Configure hotkey settings."""
    console.print("\n⌨️ Hotkey Configuration")
    console.print("=" * 30)
    
    key = input("Hotkey (default: shift): ").strip()
    key = key or "shift"
    
    description = input("Description (default: Shift key for recording): ").strip()
    description = description or f"{key.title()} key for recording"
    
    return {
        "key": key,
        "description": description
    }


def configure_general_settings() -> dict:
    """Configure general settings."""
    console.print("\n⚙️ General Settings")
    console.print("=" * 20)
    
    auto_paste = input("Auto-paste transcribed text? (y/n, default: y): ").strip().lower()
    auto_paste = auto_paste != "n"
    
    beep_feedback = input("Audio feedback for recording? (y/n, default: y): ").strip().lower()
    beep_feedback = beep_feedback != "n"
    
    temp_dir = input(f"Temporary directory (default: {Path.home() / '.voicerecorder' / 'temp'}): ").strip()
    temp_dir = temp_dir or str(Path.home() / ".voicerecorder" / "temp")
    
    return {
        "auto_paste": auto_paste,
        "beep_feedback": beep_feedback,
        "temp_directory": temp_dir
    }


def run_configuration(config_manager: ConfigManager):
    """Run interactive configuration."""
    console.print("🎤 Voice Recorder Configuration")
    console.print("=" * 50)
    
    console.print(f"Configuration will be saved to: {config_manager.get_config_path()}")
    
    # Load current config or create default
    current_config = config_manager.load_config()
    console.print(f"Current transcription mode: {current_config.transcription_config.mode.value}")
    
    # Configure transcription
    transcription_config = configure_transcription_mode()
    
    # Configure audio
    audio_config = configure_audio_settings()
    
    # Configure hotkey
    hotkey_config = configure_hotkey_settings()
    
    # Configure general settings
    general_config = configure_general_settings()
    
    # Update configuration
    updated_config = config_manager.update_config(
        transcription_config=transcription_config,
        audio_config=audio_config,
        hotkey_config=hotkey_config,
        **general_config
    )
    
    return updated_config


def show_configuration(config_manager: ConfigManager):
    """Show current configuration in a nice format."""
    config = config_manager.load_config()
    
    console.print(Panel.fit(
        Text("🎤 Voice Recorder Configuration", style="bold blue"),
        title="Configuration",
        border_style="blue"
    ))
    
    # Create table for configuration
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Description", style="green")
    
    # Audio settings
    table.add_row("Sample Rate", f"{config.audio_config.sample_rate} Hz", "Audio recording sample rate")
    table.add_row("Channels", str(config.audio_config.channels), "Number of audio channels")
    table.add_row("Chunk Size", str(config.audio_config.chunk_size), "Audio processing chunk size")
    table.add_row("Format", config.audio_config.format.value, "Audio file format")
    
    # Transcription settings
    table.add_row("Mode", config.transcription_config.mode.value, "Transcription service")
    table.add_row("Model", config.transcription_config.model_name, "Model name")
    if config.transcription_config.api_key:
        table.add_row("API Key", "***" + config.transcription_config.api_key[-4:], "OpenAI API key")
    else:
        table.add_row("API Key", "Not set", "OpenAI API key")
    table.add_row("Ollama URL", config.transcription_config.ollama_base_url, "Ollama server URL")
    
    # Hotkey settings
    table.add_row("Hotkey", config.hotkey_config.key, "Recording trigger key")
    table.add_row("Modifiers", ", ".join(config.hotkey_config.modifiers) if config.hotkey_config.modifiers else "None", "Key modifiers")
    table.add_row("Description", config.hotkey_config.description, "Hotkey description")
    
    # General settings
    table.add_row("Auto-paste", str(config.auto_paste), "Automatically paste transcribed text")
    table.add_row("Audio Feedback", str(config.beep_feedback), "Play audio feedback")
    table.add_row("Temp Directory", config.temp_directory, "Temporary file storage")
    
    console.print(table)
    
    # Show config file location
    console.print(f"\n📁 Configuration file: {config_manager.get_config_path()}")
    
    # Check temp directory
    temp_dir = Path(config.temp_directory)
    if temp_dir.exists():
        console.print(f"✅ Temp directory exists: {temp_dir}")
    else:
        console.print(f"⚠️ Temp directory does not exist: {temp_dir}", style="yellow") 