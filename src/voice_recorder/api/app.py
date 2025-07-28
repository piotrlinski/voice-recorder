"""
Main application factory and dependency injection setup.
"""

import os
import signal
import sys
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align

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
from ..infrastructure.config_manager import ConfigManager
from ..infrastructure.hotkey import PynputHotkeyListener
from ..infrastructure.session_manager import InMemorySessionManager
from ..infrastructure.text_paster import MacOSTextPaster
from ..infrastructure.transcription import TranscriptionServiceFactory
from ..services.voice_recorder_service import VoiceRecorderService


class VoiceRecorderApp:
    """Main application class with dependency injection."""

    def __init__(self, config: Optional[ApplicationConfig] = None, env_file: Optional[str] = None):
        self.console = Console()
        
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Use provided config or load from config manager
        if config is None:
            config_manager = ConfigManager()
            self.config = config_manager.load_config()
        else:
            self.config = config
        
        
        # Initialize infrastructure components
        self.audio_recorder: AudioRecorder = PyAudioRecorder()
        
        self.transcription_service: TranscriptionService = TranscriptionServiceFactory.create_service(
            self.config.transcription_config
        )
        
        self.hotkey_listener: HotkeyListener = PynputHotkeyListener()
        self.text_paster: TextPaster = MacOSTextPaster()
        self.session_manager: SessionManager = InMemorySessionManager()
        self.audio_feedback: AudioFeedback = SystemAudioFeedback(self.config.sound_config)
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
        self.console.print("\n🛑 [bold red]Shutting down voice recorder...[/bold red]")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start the voice recorder application."""
        # Only show Rich output if not in test environment
        if not os.getenv('PYTEST_CURRENT_TEST'):
            # Create startup panel
            startup_text = Text()
            startup_text.append("🎤 Voice Recorder Application Starting...\n", style="bold blue")
            startup_text.append(f"⌨️  Hotkey: {self.config.hotkey_config.key}\n", style="cyan")
            startup_text.append(f"🎵 Audio: {self.config.audio_config.sample_rate}Hz, {self.config.audio_config.channels} channel(s)\n", style="cyan")
            startup_text.append(f"🤖 Transcription: {self.config.transcription_config.mode.value}\n", style="cyan")
            startup_text.append(f"🧠 Model: {self.config.transcription_config.model_name}\n", style="cyan")
            startup_text.append(f"📋 Auto-paste: {self.config.auto_paste}\n", style="cyan")
            startup_text.append(f"🔔 Sound feedback: {self.config.sound_config.enabled}", style="cyan")
            
            startup_panel = Panel(
                startup_text,
                title="[bold green]Voice Recorder Configuration[/bold green]",
                border_style="green",
                padding=(1, 2)
            )
            self.console.print(startup_panel)
        
        try:
            self.voice_recorder_service.start()
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                # Success panel
                success_text = Text()
                success_text.append("✅ Voice recorder started successfully!\n", style="bold green")
                success_text.append("💡 Press Ctrl+C to stop", style="yellow")
                
                success_panel = Panel(
                    success_text,
                    title="[bold green]Ready to Record[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                )
                self.console.print(success_panel)
            
            # Keep the application running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Failed to start voice recorder: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Startup Error[/bold red]",
                border_style="red",
                padding=(1, 2)
            )
            self.console.print(error_panel)
            raise

    def stop(self):
        """Stop the voice recorder application."""
        self.console.print("🛑 [bold yellow]Stopping voice recorder...[/bold yellow]")
        try:
            self.voice_recorder_service.stop()
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                stop_text = Text()
                stop_text.append("✅ Voice recorder stopped successfully!", style="bold green")
                
                stop_panel = Panel(
                    stop_text,
                    title="[bold green]Shutdown Complete[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                )
                self.console.print(stop_panel)
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Error stopping voice recorder: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Shutdown Error[/bold red]",
                border_style="red",
                padding=(1, 2)
            )
            self.console.print(error_panel)


def create_app(config: Optional[ApplicationConfig] = None, env_file: Optional[str] = None) -> VoiceRecorderApp:
    """Factory function to create the voice recorder application."""
    return VoiceRecorderApp(config, env_file=env_file)


def main():
    """Main entry point for the voice recorder application."""
    console = Console()
    try:
        app = create_app()
        app.start()
    except KeyboardInterrupt:
        console.print("\n👋 [bold yellow]Application interrupted by user[/bold yellow]")
    except Exception as e:
        error_text = Text()
        error_text.append(f"💥 Application error: {e}", style="bold red")
        
        error_panel = Panel(
            error_text,
            title="[bold red]Fatal Error[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(error_panel)
        sys.exit(1)


if __name__ == "__main__":
    main()
