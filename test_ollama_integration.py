#!/usr/bin/env python3
"""
Test script to verify Ollama integration.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from voice_recorder.domain.models import TranscriptionConfig, TranscriptionMode
from voice_recorder.infrastructure.transcription import (
    OllamaWhisperTranscriptionService,
    OllamaModelTranscriptionService
)


def test_ollama_connection():
    """Test Ollama connection and list available models."""
    print("🔍 Testing Ollama connection...")
    
    try:
        import ollama
        
        # Test basic connection
        models = ollama.list()
        print(f"✅ Ollama server connected successfully")
        print(f"📋 Available models: {[model['name'] for model in models['models']]}")
        
        return True
    except ImportError:
        print("❌ Ollama Python client not installed. Run: pip install ollama")
        return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("Make sure Ollama is running: brew install ollama && ollama serve")
        return False


def test_ollama_whisper_service():
    """Test Ollama Whisper transcription service."""
    print("\n🤖 Testing Ollama Whisper service...")
    
    try:
        service = OllamaWhisperTranscriptionService()
        print("✅ Ollama Whisper service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Ollama Whisper service failed: {e}")
        return False


def test_ollama_model_service():
    """Test Ollama model transcription service."""
    print("\n🦙 Testing Ollama model service...")
    
    try:
        # Test with a common model name
        service = OllamaModelTranscriptionService("llama3.2")
        print("✅ Ollama model service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Ollama model service failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Ollama Integration Test")
    print("=" * 40)
    
    # Test connection
    connection_ok = test_ollama_connection()
    
    if connection_ok:
        # Test services
        whisper_ok = test_ollama_whisper_service()
        model_ok = test_ollama_model_service()
        
        print(f"\n📊 Test Results:")
        print(f"   Connection: {'✅' if connection_ok else '❌'}")
        print(f"   Whisper Service: {'✅' if whisper_ok else '❌'}")
        print(f"   Model Service: {'✅' if model_ok else '❌'}")
        
        if connection_ok and whisper_ok and model_ok:
            print(f"\n🎉 All tests passed! Ollama integration is working correctly.")
        else:
            print(f"\n⚠️  Some tests failed. Check the error messages above.")
    else:
        print(f"\n❌ Cannot test services without Ollama connection.")


if __name__ == "__main__":
    main() 