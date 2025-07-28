#!/usr/bin/env python3
"""
Example script showing how to use different transcription modes.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from voice_recorder.domain.models import (
    ApplicationConfig, 
    TranscriptionConfig, 
    TranscriptionMode
)
from voice_recorder.api.app import create_app


def example_openai_whisper():
    """Example using OpenAI Whisper."""
    print("🔑 Using OpenAI Whisper")
    
    config = ApplicationConfig(
        transcription_config=TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER,
            model_name="whisper-1",
            api_key="your-openai-api-key-here"
        )
    )
    
    app = create_app(config)
    return app


def example_local_whisper():
    """Example using Local Whisper."""
    print("🏠 Using Local Whisper")
    
    config = ApplicationConfig(
        transcription_config=TranscriptionConfig(
            mode=TranscriptionMode.LOCAL_WHISPER,
            model_name="base"  # tiny, base, small, medium, large
        )
    )
    
    app = create_app(config)
    return app


def example_ollama_whisper():
    """Example using Ollama Whisper."""
    print("🤖 Using Ollama Whisper")
    print("Note: Make sure Ollama is running and you have pulled the whisper model:")
    print("  brew install ollama")
    print("  ollama pull whisper")
    print("  pip install ollama")
    
    config = ApplicationConfig(
        transcription_config=TranscriptionConfig(
            mode=TranscriptionMode.OLLAMA_WHISPER,
            model_name="whisper",
            ollama_base_url="http://localhost:11434"
        )
    )
    
    app = create_app(config)
    return app


def example_ollama_llama():
    """Example using Ollama with Llama model."""
    print("🦙 Using Ollama with Llama model")
    print("Note: Make sure Ollama is running and you have pulled the llama3.2 model:")
    print("  brew install ollama")
    print("  ollama pull llama3.2")
    print("  pip install ollama")
    
    config = ApplicationConfig(
        transcription_config=TranscriptionConfig(
            mode=TranscriptionMode.OLLAMA_MODEL,
            model_name="llama3.2",
            ollama_base_url="http://localhost:11434"
        )
    )
    
    app = create_app(config)
    return app


def example_ollama_deepseek():
    """Example using Ollama with DeepSeek model."""
    print("🧠 Using Ollama with DeepSeek model")
    print("Note: Make sure Ollama is running and you have pulled the deepseek-coder model:")
    print("  brew install ollama")
    print("  ollama pull deepseek-coder")
    print("  pip install ollama")
    
    config = ApplicationConfig(
        transcription_config=TranscriptionConfig(
            mode=TranscriptionMode.OLLAMA_MODEL,
            model_name="deepseek-coder",
            ollama_base_url="http://localhost:11434"
        )
    )
    
    app = create_app(config)
    return app


def main():
    """Main function to demonstrate different transcription modes."""
    print("🎤 Voice Recorder Transcription Examples")
    print("=" * 50)
    
    examples = [
        ("OpenAI Whisper", example_openai_whisper),
        ("Local Whisper", example_local_whisper),
        ("Ollama Whisper", example_ollama_whisper),
        ("Ollama Llama", example_ollama_llama),
        ("Ollama DeepSeek", example_ollama_deepseek),
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    try:
        choice = int(input("\nSelect example (1-5): ")) - 1
        if 0 <= choice < len(examples):
            name, func = examples[choice]
            print(f"\nRunning: {name}")
            app = func()
            
            # Start the application
            print("Starting voice recorder...")
            print("Press Shift to record, release to stop.")
            print("Press Ctrl+C to exit.")
            
            app.start()
        else:
            print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 