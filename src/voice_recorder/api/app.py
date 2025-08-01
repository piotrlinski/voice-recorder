"""
Voice recorder application entry point.
"""

import os
import signal
import sys
import time
from typing import Optional


from ..domain.interfaces import (
    AudioRecorderInterface,
    AudioFeedback,
    HotkeyListenerInterface,
    SessionManagerInterface,
    TextPasterInterface,
    TranscriptionServiceInterface,
    EnhancedTranscriptionServiceInterface,
)
from ..domain.models import ApplicationConfig
from ..infrastructure.audio_feedback import SystemAudioFeedback
from ..infrastructure.audio_recorder import PyAudioRecorder
from ..infrastructure.config_manager import ConfigManager
from ..infrastructure.hotkey import PynputHotkeyListener
from ..infrastructure.logging_adapter import LoggingAdapter
from ..infrastructure.session_manager import InMemorySessionManager
from ..infrastructure.text_paster import MacOSTextPaster
from ..infrastructure.transcription.factory import TranscriptionServiceFactory
from ..services.voice_recorder_service import VoiceRecorderService


class VoiceRecorderApp:
    """Main voice recorder application class."""

    def __init__(self, config: Optional[ApplicationConfig] = None):
        """Initialize the voice recorder application."""

        # Initialize logging
        self.console = LoggingAdapter()

        # Load configuration
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.load_config()
        self.config = config

        # Initialize infrastructure components
        self.audio_recorder: AudioRecorderInterface = PyAudioRecorder(
            console=self.console
        )
        self.transcription_service: TranscriptionServiceInterface = (
            TranscriptionServiceFactory.create_service(
                config.transcription, console=self.console
            )
        )
        self.enhanced_transcription_service: EnhancedTranscriptionServiceInterface = (
            TranscriptionServiceFactory.create_enhanced_service(
                config.transcription, console=self.console
            )
        )
        self.hotkey_listener: HotkeyListenerInterface = PynputHotkeyListener(
            console=self.console
        )
        self.text_paster: TextPasterInterface = MacOSTextPaster(console=self.console)
        self.session_manager: SessionManagerInterface = InMemorySessionManager()
        self.audio_feedback: AudioFeedback = SystemAudioFeedback(console=self.console)

        # Initialize service layer
        self.voice_recorder_service = VoiceRecorderService(
            audio_recorder=self.audio_recorder,
            transcription_service=self.transcription_service,
            enhanced_transcription_service=self.enhanced_transcription_service,
            hotkey_listener=self.hotkey_listener,
            text_paster=self.text_paster,
            session_manager=self.session_manager,
            audio_feedback=self.audio_feedback,
            config=self.config,
            console=self.console,
        )

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.console.info("Shutting down voice recorder...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start the voice recorder application."""
        # Log startup configuration
        self.console.info("Voice Recorder Application Starting...")
        self.console.info(f"Basic Key: {self.config.controls.basic_key}")
        self.console.info(f"Enhanced Key: {self.config.controls.enhanced_key}")
        self.console.info(
            f"Audio: {self.config.audio.sample_rate}Hz, {self.config.audio.channels} channel(s)"
        )
        self.console.info(f"Transcription: {self.config.transcription.mode.value}")
        self.console.info(f"Auto-paste: {self.config.general.auto_paste}")
        self.console.info(f"Sound feedback: {self.config.sound.enabled}")

        try:
            self.voice_recorder_service.start()
            self.console.info("Voice recorder started successfully!")
            self.console.info("Press Ctrl+C to stop")

            # Keep the application running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        except Exception as e:
            self.console.error(f"Failed to start voice recorder: {e}")
            raise

    def stop(self):
        """Stop the voice recorder application."""
        self.console.info("Stopping voice recorder...")
        try:
            self.voice_recorder_service.stop()
            self.console.info("Voice recorder stopped successfully!")
        except Exception as e:
            self.console.error(f"Error stopping voice recorder: {e}")


def create_app(config: Optional[ApplicationConfig] = None) -> VoiceRecorderApp:
    """Factory function to create the voice recorder application."""
    return VoiceRecorderApp(config)


def main():
    """Main entry point for the voice recorder application."""
    # Import here to avoid circular imports
    from ..cli.commands import main as cli_main

    sys.exit(cli_main())


if __name__ == "__main__":
    main()
