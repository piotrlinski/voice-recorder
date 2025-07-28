"""
Main voice recorder service that orchestrates recording, transcription, and pasting.
"""

from datetime import datetime
from typing import Optional

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
            print(f"Recording started (Session: {session_id})...")
        except Exception as e:
            print(f"Error starting recording: {e}")
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
                print("No audio file generated")
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
                return
            # Update session with audio file path
            self.current_session.audio_file_path = audio_file_path
            self.session_manager.update_session(self.current_session)
            # Audio feedback
            self.audio_feedback.play_stop_beep()
            print("Recording stopped. Transcribing...")
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
                        print(f"Pasted: {transcription_result.text.strip()}")
                    else:
                        print(f"Failed to paste: {transcription_result.text.strip()}")
                else:
                    print(f"Transcript: {transcription_result.text.strip()}")
            else:
                print("No transcript generated")
            # Mark session as complete
            self.current_session.state = RecordingState.IDLE
            self.session_manager.update_session(self.current_session)
        except Exception as e:
            print(f"Error during processing: {e}")
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
