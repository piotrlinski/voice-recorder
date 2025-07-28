"""
Main application factory and dependency injection setup.
"""

import os
import signal
import sys
from typing import Optional

from dotenv import load_dotenv

from ..domain.interfaces import (
    AudioFeedback,
    AudioRecorder,
    HotkeyListener,
    SessionManager,
    TextPaster,
    TranscriptionService,
)
from ..domain.models import ApplicationConfig
from ..infrastructure.audio_feedback import SystemAudioFeedback
from ..infrastructure.audio_recorder import PyAudioRecorder
from ..infrastructure.hotkey import PynputHotkeyListener
from ..infrastructure.session_manager import InMemorySessionManager
from ..infrastructure.text_paster import MacOSTextPaster
from ..infrastructure.transcription import TranscriptionServiceFactory
from ..services.voice_recorder_service import VoiceRecorderService


class VoiceRecorderApp:
    """Main application class with dependency injection."""

    def __init__(self, config: Optional[ApplicationConfig] = None):
        # Load environment variables
        load_dotenv("my.env")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY not set in my.env or environment")
        # Use provided config or create default
        self.config = config or ApplicationConfig()
        # Initialize infrastructure components
        self.audio_recorder: AudioRecorder = PyAudioRecorder()
        
        # Create transcription service based on configuration
        if self.config.transcription_config.mode.value == "openai_whisper":
            # Set API key for OpenAI mode
            self.config.transcription_config.api_key = self.openai_api_key
        
        self.transcription_service: TranscriptionService = TranscriptionServiceFactory.create_service(
            self.config.transcription_config
        )
        
        self.hotkey_listener: HotkeyListener = PynputHotkeyListener()
        self.text_paster: TextPaster = MacOSTextPaster()
        self.session_manager: SessionManager = InMemorySessionManager()
        self.audio_feedback: AudioFeedback = SystemAudioFeedback()
        # Initialize main service
        self.voice_recorder_service = VoiceRecorderService(
            audio_recorder=self.audio_recorder,
            transcription_service=self.transcription_service,
            hotkey_listener=self.hotkey_listener,
            text_paster=self.text_paster,
            session_manager=self.session_manager,
            audio_feedback=self.audio_feedback,
            config=self.config,
        )
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\nShutting down voice recorder...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start the voice recorder application."""
        print("Voice Recorder Application Starting...")
        print(f"Hotkey: {self.config.hotkey_config.key}")
        print(
            f"Audio Config: {self.config.audio_config.sample_rate}Hz, {self.config.audio_config.channels} channel(s)"
        )
        print(f"Transcription Mode: {self.config.transcription_config.mode.value}")
        print(f"Model: {self.config.transcription_config.model_name}")
        print(f"Auto-paste: {self.config.auto_paste}")
        print(f"Audio feedback: {self.config.beep_feedback}")
        print("-" * 50)
        try:
            self.voice_recorder_service.start()
            print("Voice recorder started successfully!")
            print("Press Ctrl+C to stop")
            # Keep the application running
            try:
                while True:
                    import time

                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        except Exception as e:
            print(f"Failed to start voice recorder: {e}")
            raise

    def stop(self):
        """Stop the voice recorder application."""
        print("Stopping voice recorder...")
        try:
            self.voice_recorder_service.stop()
            print("Voice recorder stopped successfully!")
        except Exception as e:
            print(f"Error stopping voice recorder: {e}")


def create_app(config: Optional[ApplicationConfig] = None) -> VoiceRecorderApp:
    """Factory function to create the voice recorder application."""
    return VoiceRecorderApp(config)


def main():
    """Main entry point for the voice recorder application."""
    try:
        app = create_app()
        app.start()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
