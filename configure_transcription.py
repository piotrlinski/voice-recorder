#!/usr/bin/env python3
"""
Configuration script for voice recorder transcription modes.
"""

import os
import sys
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from voice_recorder.domain.models import (
    ApplicationConfig, 
    TranscriptionConfig, 
    TranscriptionMode
)


def get_user_choice(prompt: str, options: list) -> int:
    """Get user choice from a list of options."""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")


def configure_openai_mode() -> TranscriptionConfig:
    """Configure OpenAI Whisper mode."""
    print("\n=== OpenAI Whisper Configuration ===")
    
    # Check if API key exists
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Enter your OpenAI API key: ").strip()
        if not api_key:
            print("OpenAI API key is required for this mode.")
            return None
    
    return TranscriptionConfig(
        mode=TranscriptionMode.OPENAI_WHISPER,
        model_name="whisper-1",
        api_key=api_key
    )


def configure_local_whisper_mode() -> TranscriptionConfig:
    """Configure Local Whisper mode."""
    print("\n=== Local Whisper Configuration ===")
    print("This mode uses Whisper.cpp for local transcription.")
    print("Make sure you have installed: pip install whisper-cpp-python")
    
    models = ["tiny", "base", "small", "medium", "large"]
    model_choice = get_user_choice(
        "Select Whisper model size (larger = more accurate but slower):",
        [f"{model} ({'faster' if model in ['tiny', 'base'] else 'more accurate'})" for model in models]
    )
    
    return TranscriptionConfig(
        mode=TranscriptionMode.LOCAL_WHISPER,
        model_name=models[model_choice]
    )


def configure_ollama_whisper_mode() -> TranscriptionConfig:
    """Configure Ollama Whisper mode."""
    print("\n=== Ollama Whisper Configuration ===")
    print("This mode uses Ollama with Whisper model.")
    print("Make sure Ollama is running and you have pulled the whisper model:")
    print("  brew install ollama")
    print("  ollama pull whisper")
    print("  pip install ollama")
    
    base_url = input("Enter Ollama server URL (default: http://localhost:11434): ").strip()
    if not base_url:
        base_url = "http://localhost:11434"
    
    return TranscriptionConfig(
        mode=TranscriptionMode.OLLAMA_WHISPER,
        model_name="whisper",
        ollama_base_url=base_url
    )


def configure_ollama_model_mode() -> TranscriptionConfig:
    """Configure Ollama with custom model mode."""
    print("\n=== Ollama Model Configuration ===")
    print("This mode uses any Ollama model for transcription.")
    print("Make sure Ollama is running and you have pulled your desired model:")
    print("  ollama pull llama3.2")
    print("  ollama pull deepseek-coder")
    print("  ollama pull codellama")
    print("  pip install ollama")
    
    base_url = input("Enter Ollama server URL (default: http://localhost:11434): ").strip()
    if not base_url:
        base_url = "http://localhost:11434"
    
    model_name = input("Enter Ollama model name (e.g., llama3.2, deepseek-coder): ").strip()
    if not model_name:
        print("Model name is required.")
        return None
    
    return TranscriptionConfig(
        mode=TranscriptionMode.OLLAMA_MODEL,
        model_name=model_name,
        ollama_base_url=base_url
    )


def main():
    """Main configuration function."""
    print("🎤 Voice Recorder Transcription Configuration")
    print("=" * 50)
    
    # Show available modes
    modes = [
        "OpenAI Whisper (cloud-based, requires API key)",
        "Local Whisper (offline, requires model download)",
        "Ollama Whisper (local, requires Ollama + whisper model)",
        "Ollama Custom Model (local, any Ollama model)"
    ]
    
    choice = get_user_choice("Select transcription mode:", modes)
    
    config = None
    if choice == 0:
        config = configure_openai_mode()
    elif choice == 1:
        config = configure_local_whisper_mode()
    elif choice == 2:
        config = configure_ollama_whisper_mode()
    elif choice == 3:
        config = configure_ollama_model_mode()
    
    if config is None:
        print("\n❌ Configuration failed. Please try again.")
        return
    
    # Create application config
    app_config = ApplicationConfig(transcription_config=config)
    
    # Save configuration
    config_file = "voice_recorder_config.py"
    with open(config_file, "w") as f:
        f.write(f"""# Voice Recorder Configuration
# Generated by configure_transcription.py

from voice_recorder.domain.models import ApplicationConfig, TranscriptionConfig, TranscriptionMode

# Application configuration
config = ApplicationConfig(
    transcription_config=TranscriptionConfig(
        mode=TranscriptionMode.{config.mode.value.upper()},
        model_name="{config.model_name}",
        api_key={"'" + config.api_key + "'" if config.api_key else "None"},
        ollama_base_url="{config.ollama_base_url}"
    )
)

# Usage:
# from voice_recorder.api.app import create_app
# app = create_app(config)
# app.start()
""")
    
    print(f"\n✅ Configuration saved to {config_file}")
    print(f"📋 Transcription Mode: {config.mode.value}")
    print(f"🤖 Model: {config.model_name}")
    
    if config.mode == TranscriptionMode.OPENAI_WHISPER:
        print("🔑 API Key: Configured")
    elif config.mode in [TranscriptionMode.OLLAMA_WHISPER, TranscriptionMode.OLLAMA_MODEL]:
        print(f"🌐 Ollama URL: {config.ollama_base_url}")
    
    print(f"\n📝 To use this configuration:")
    print(f"   python {config_file}")
    print(f"   # Then import and use the config")


if __name__ == "__main__":
    main() 