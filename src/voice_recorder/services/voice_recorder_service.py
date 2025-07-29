"""
Voice recorder service implementation.
"""

import os
from datetime import datetime
from typing import Optional

from rich.panel import Panel
from rich.text import Text

from ..domain.interfaces import (
    AudioRecorderInterface,
    AudioFeedback,
    HotkeyListenerInterface,
    SessionManagerInterface,
    TextPasterInterface,
    TranscriptionServiceInterface,
    ConsoleInterface,
)
from ..domain.models import ApplicationConfig, RecordingSession, RecordingState


class VoiceRecorderService:
    """Main voice recorder service orchestrating all components."""

    def __init__(
        self,
        audio_recorder: AudioRecorderInterface,
        transcription_service: TranscriptionServiceInterface,
        hotkey_listener: HotkeyListenerInterface,
        text_paster: TextPasterInterface,
        session_manager: SessionManagerInterface,
        audio_feedback: AudioFeedback,
        config: ApplicationConfig,
        console: ConsoleInterface,
    ):
        """Initialize the voice recorder service."""
        self.audio_recorder = audio_recorder
        self.transcription_service = transcription_service
        self.hotkey_listener = hotkey_listener
        self.text_paster = text_paster
        self.session_manager = session_manager
        self.audio_feedback = audio_feedback
        self.config = config
        self.console = console
        
        self.current_session: Optional[RecordingSession] = None
        self.is_recording = False
        self.hotkey_pressed = False

    def start(self) -> None:
        """Start the voice recorder service."""
        try:
            # Set up the callbacks for the hotkey listener
            self.hotkey_listener.set_callbacks(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.hotkey_listener.start_listening()
        except Exception as e:
            self.console.print_error(f"Failed to start hotkey listener: {e}")
            raise

    def stop(self) -> None:
        """Stop the voice recorder service."""
        try:
            if self.is_recording:
                self._stop_current_recording()
            self.hotkey_listener.stop_listening()
        except Exception as e:
            self.console.print_error(f"Error stopping service: {e}")

    def _is_hotkey_pressed(self, key) -> bool:
        """Check if the pressed key matches the configured hotkey."""
        # Handle different key formats
        if hasattr(key, 'char') and key.char:
            # Character key
            return key.char.lower() == self.config.hotkey_config.key.lower()
        elif hasattr(key, 'name'):
            # Named key (like 'shift', 'ctrl', etc.)
            return key.name.lower() == self.config.hotkey_config.key.lower()
        else:
            # String comparison as fallback
            return str(key).lower() == self.config.hotkey_config.key.lower()

    def _on_key_press(self, key) -> None:
        """Handle key press events."""
        if self._is_hotkey_pressed(key):
            self.hotkey_pressed = True
            if not self.is_recording:
                self._start_recording()

    def _on_key_release(self, key) -> None:
        """Handle key release events."""
        if self._is_hotkey_pressed(key):
            self.hotkey_pressed = False
            if self.is_recording:
                self._stop_recording_and_process()

    def _start_recording(self) -> None:
        """Start recording audio."""
        if self.is_recording:
            return
        
        try:
            self.is_recording = True
            
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
                self.current_session.state = RecordingState.COMPLETED
                self.session_manager.update_session(self.current_session)
                
                # Auto-paste if enabled
                if self.config.auto_paste:
                    success = self.text_paster.paste_text(transcription_result.text)
                    if success:
                        paste_text = Text()
                        paste_text.append("📋 Text pasted successfully", style="bold green")
                        
                        paste_panel = Panel(
                            paste_text,
                            title="[bold green]Text Pasted[/bold green]",
                            border_style="green",
                            padding=(0, 1)
                        )
                        self.console.print(paste_panel)
                    else:
                        paste_error_text = Text()
                        paste_error_text.append("⚠️ Failed to paste text", style="bold yellow")
                        
                        paste_error_panel = Panel(
                            paste_error_text,
                            title="[bold yellow]Paste Error[/bold yellow]",
                            border_style="yellow",
                            padding=(0, 1)
                        )
                        self.console.print(paste_error_panel)
                
                # Success notification
                success_text = Text()
                success_text.append("✅ Transcription completed", style="bold green")
                success_text.append(f"\n📝 Text: {transcription_result.text[:100]}...", style="cyan")
                
                success_panel = Panel(
                    success_text,
                    title="[bold green]Transcription Complete[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(success_panel)
            else:
                # No transcription result
                no_transcript_text = Text()
                no_transcript_text.append("⚠️ No transcription generated", style="bold yellow")
                
                no_transcript_panel = Panel(
                    no_transcript_text,
                    title="[bold yellow]Transcription Issue[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(no_transcript_panel)
                
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
            
            # Clean up audio file
            try:
                if os.path.exists(audio_file_path):
                    os.unlink(audio_file_path)
            except Exception as e:
                self.console.print_warning(f"Failed to clean up audio file: {e}")
            
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Error processing recording: {e}", style="bold red")
            
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
        finally:
            self.is_recording = False
            self.current_session = None

    def _stop_current_recording(self) -> None:
        """Stop the current recording if active."""
        if self.is_recording and self.current_session:
            self._stop_recording_and_process()

    def get_current_session(self) -> Optional[RecordingSession]:
        """Get the current recording session."""
        return self.current_session

    def get_session_history(self) -> list[RecordingSession]:
        """Get all recording sessions."""
        return self.session_manager.get_all_sessions()
