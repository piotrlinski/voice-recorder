"""
Main voice recorder service that orchestrates recording, transcription, and pasting.
"""

import os
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from ..domain.interfaces import (
    AudioFeedback,
    AudioRecorder,
    HotkeyListener,
    SessionManager,
    TextPaster,
    TranscriptionService,
)
from ..domain.models import ApplicationConfig, RecordingSession, RecordingState


class VoiceRecorderService:
    """
    Main service that orchestrates voice recording, transcription, and text pasting.
    This service implements the core business logic and coordinates between
    different infrastructure components.
    """

    def __init__(
        self,
        audio_recorder: AudioRecorder,
        transcription_service: TranscriptionService,
        hotkey_listener: HotkeyListener,
        text_paster: TextPaster,
        session_manager: SessionManager,
        audio_feedback: AudioFeedback,
        config: ApplicationConfig,
    ):
        self.audio_recorder = audio_recorder
        self.transcription_service = transcription_service
        self.hotkey_listener = hotkey_listener
        self.text_paster = text_paster
        self.session_manager = session_manager
        self.audio_feedback = audio_feedback
        self.config = config
        self.current_session: Optional[RecordingSession] = None
        self.is_running = False
        self.console = Console()

    def start(self) -> None:
        """Start the voice recorder service."""
        self.is_running = True
        self.hotkey_listener.start_listening(
            on_press=self._on_key_press, on_release=self._on_key_release
        )

    def stop(self) -> None:
        """Stop the voice recorder service."""
        self.is_running = False
        self.hotkey_listener.stop_listening()
        # Stop any active recording
        if (
            self.current_session
            and self.current_session.state == RecordingState.RECORDING
        ):
            self._stop_current_recording()

    def _on_key_press(self, key) -> None:
        """Handle key press event."""
        if not self.is_running:
            return
        # Check if the pressed key matches our hotkey configuration
        if self._is_hotkey_pressed(key):
            self._start_recording()

    def _on_key_release(self, key) -> None:
        """Handle key release event."""
        if not self.is_running:
            return
        # Check if the released key matches our hotkey configuration
        if self._is_hotkey_pressed(key):
            self._stop_recording_and_process()

    def _is_hotkey_pressed(self, key) -> bool:
        """Check if the pressed key matches the configured hotkey."""
        # Simple implementation - can be extended for modifier keys
        hotkey_name = self.config.hotkey_config.key.lower()
        return str(key).lower() == f"key.{hotkey_name}"

    def _start_recording(self) -> None:
        """Start a new recording session."""
        if (
            self.current_session
            and self.current_session.state == RecordingState.RECORDING
        ):
            return  # Already recording
        try:
            # Create new session
            self.current_session = self.session_manager.create_session()
            self.current_session.state = RecordingState.RECORDING
            self.current_session.start_time = datetime.now()
            # Start audio recording
            session_id = self.audio_recorder.start_recording(self.config.audio_config)
            self.current_session.id = session_id
            # Update session
            self.session_manager.update_session(self.current_session)
            # Audio feedback
            self.audio_feedback.play_start_beep()
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                # Recording started notification
                recording_text = Text()
                recording_text.append("🎙️ Recording started", style="bold green")
                recording_text.append(f" (Session: {session_id})", style="cyan")
                
                recording_panel = Panel(
                    recording_text,
                    title="[bold green]Recording Active[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(recording_panel)
            
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Error starting recording: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Recording Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            
            if self.current_session:
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)

    def _stop_recording_and_process(self) -> None:
        """Stop recording and process the audio."""
        if (
            not self.current_session
            or self.current_session.state != RecordingState.RECORDING
        ):
            return
        try:
            # Update session state
            self.current_session.state = RecordingState.PROCESSING
            self.current_session.end_time = datetime.now()
            self.session_manager.update_session(self.current_session)
            # Stop recording
            audio_file_path = self.audio_recorder.stop_recording(
                self.current_session.id
            )
            if not audio_file_path:
                no_audio_text = Text()
                no_audio_text.append("⚠️ No audio file generated", style="bold yellow")
                
                no_audio_panel = Panel(
                    no_audio_text,
                    title="[bold yellow]Recording Issue[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(no_audio_panel)
                
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
                return
            # Update session with audio file path
            self.current_session.audio_file_path = audio_file_path
            self.session_manager.update_session(self.current_session)
            # Audio feedback
            self.audio_feedback.play_stop_beep()
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                # Processing notification
                processing_text = Text()
                processing_text.append("🔄 Recording stopped. Transcribing...", style="bold blue")
                
                processing_panel = Panel(
                    processing_text,
                    title="[bold blue]Processing Audio[/bold blue]",
                    border_style="blue",
                    padding=(0, 1)
                )
                self.console.print(processing_panel)
            
            # Transcribe audio
            transcription_result = self.transcription_service.transcribe(
                audio_file_path
            )
            if transcription_result and transcription_result.text.strip():
                # Update session with transcript
                self.current_session.transcript = transcription_result.text
                self.current_session.confidence = transcription_result.confidence
                self.session_manager.update_session(self.current_session)
                # Paste text if auto-paste is enabled
                if self.config.auto_paste:
                    success = self.text_paster.paste_text(
                        transcription_result.text.strip()
                    )
                    if success:
                        paste_text = Text()
                        paste_text.append("📋 Pasted: ", style="bold green")
                        paste_text.append(transcription_result.text.strip(), style="white")
                        
                        paste_panel = Panel(
                            paste_text,
                            title="[bold green]Text Pasted[/bold green]",
                            border_style="green",
                            padding=(0, 1)
                        )
                        self.console.print(paste_panel)
                    else:
                        failed_text = Text()
                        failed_text.append("❌ Failed to paste: ", style="bold red")
                        failed_text.append(transcription_result.text.strip(), style="white")
                        
                        failed_panel = Panel(
                            failed_text,
                            title="[bold red]Paste Failed[/bold red]",
                            border_style="red",
                            padding=(0, 1)
                        )
                        self.console.print(failed_panel)
                else:
                    transcript_text = Text()
                    transcript_text.append("📝 Transcript: ", style="bold cyan")
                    transcript_text.append(transcription_result.text.strip(), style="white")
                    
                    transcript_panel = Panel(
                        transcript_text,
                        title="[bold cyan]Transcription Complete[/bold cyan]",
                        border_style="cyan",
                        padding=(0, 1)
                    )
                    self.console.print(transcript_panel)
            else:
                no_transcript_text = Text()
                no_transcript_text.append("⚠️ No transcript generated", style="bold yellow")
                
                no_transcript_panel = Panel(
                    no_transcript_text,
                    title="[bold yellow]Transcription Issue[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(no_transcript_panel)
            # Mark session as complete
            self.current_session.state = RecordingState.IDLE
            self.session_manager.update_session(self.current_session)
        except Exception as e:
            error_text = Text()
            error_text.append(f"💥 Error during processing: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Processing Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            
            if self.current_session:
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)

    def _stop_current_recording(self) -> None:
        """Stop the current recording without processing."""
        if (
            self.current_session
            and self.current_session.state == RecordingState.RECORDING
        ):
            self.audio_recorder.stop_recording(self.current_session.id)
            self.current_session.state = RecordingState.IDLE
            self.session_manager.update_session(self.current_session)

    def get_current_session(self) -> Optional[RecordingSession]:
        """Get the current recording session."""
        return self.current_session

    def get_session_history(self) -> list[RecordingSession]:
        """Get session history (to be implemented by session manager)."""
        # This would be implemented by the session manager
        return []
