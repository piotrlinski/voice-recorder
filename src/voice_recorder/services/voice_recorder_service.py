"""
Voice recorder service implementation.
"""

import os
from datetime import datetime
from typing import Optional


from ..domain.interfaces import (
    AudioRecorderInterface,
    AudioFeedback,
    HotkeyListenerInterface,
    SessionManagerInterface,
    TextPasterInterface,
    TranscriptionServiceInterface,
    EnhancedTranscriptionServiceInterface,
    ConsoleInterface,
)
from ..domain.models import (
    ApplicationConfig,
    RecordingSession,
    RecordingState,
    EnhancedTranscriptionResult,
)


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
        enhanced_transcription_service: (
            EnhancedTranscriptionServiceInterface | None
        ) = None,
    ):
        """Initialize the voice recorder service."""
        self.audio_recorder = audio_recorder
        self.transcription_service = transcription_service
        self.enhanced_transcription_service = enhanced_transcription_service
        self.hotkey_listener = hotkey_listener
        self.text_paster = text_paster
        self.session_manager = session_manager
        self.audio_feedback = audio_feedback
        self.config = config
        self.console = console

        self.current_session: Optional[RecordingSession] = None
        self.is_recording = False
        self.hotkey_pressed = False
        self.recording_type = "basic"  # Track whether recording is basic or enhanced

    def start(self) -> None:
        """Start the voice recorder service."""
        try:
            # Set up callbacks for separate basic and enhanced keys
            self.hotkey_listener.set_callbacks(
                on_press=self._on_any_key_press, on_release=self._on_any_key_release
            )

            self.hotkey_listener.start_listening()
        except Exception as e:
            self.console.error(f"Failed to start hotkey listener: {e}")
            raise

    def stop(self) -> None:
        """Stop the voice recorder service."""
        try:
            if self.is_recording:
                self._stop_current_recording()
            self.hotkey_listener.stop_listening()
        except Exception as e:
            self.console.error(f"Error stopping service: {e}")

    def _is_basic_key_pressed(self, key) -> bool:
        """Check if the pressed key matches the basic transcription key."""
        return self._key_matches_config(key, self.config.controls.basic_key)

    def _is_enhanced_key_pressed(self, key) -> bool:
        """Check if the pressed key matches the enhanced transcription key."""
        return self._key_matches_config(key, self.config.controls.enhanced_key)

    def _key_matches_config(self, key, configured_key: str) -> bool:
        """Check if a key matches the configured key."""
        configured_key = configured_key.lower()

        # Debug logging
        if self.console:
            self.console.debug(
                f"Key pressed: {key}, checking against: {configured_key}"
            )

        # Handle different key formats
        if hasattr(key, "char") and key.char:
            # Character key
            key_char = key.char.lower()
            return key_char == configured_key
        elif hasattr(key, "name"):
            # Named key (like 'shift', 'ctrl', etc.)
            key_name = key.name.lower()

            # Handle special key mappings for pynput
            key_mappings = {
                "shift_r": ["shift_r", "right_shift"],
                "shift_l": ["shift_l", "left_shift"],
                "ctrl": ["ctrl", "ctrl_l", "left_ctrl"],
                "ctrl_l": ["ctrl", "ctrl_l", "left_ctrl"],
                "ctrl_r": ["ctrl_r", "right_ctrl"],
                "cmd": ["cmd", "cmd_l", "left_cmd", "super"],
                "alt": ["alt", "alt_l", "left_alt"],
            }

            # Check if configured key has mappings
            if configured_key in key_mappings:
                is_match = key_name in key_mappings[configured_key]
                if self.console:
                    self.console.debug(f"Key match: {is_match} (key_name: {key_name})")
                return is_match
            else:
                is_match = key_name == configured_key
                if self.console:
                    self.console.debug(f"Direct key match: {is_match}")
                return is_match
        else:
            # String comparison as fallback
            key_str = str(key).lower()
            return key_str == configured_key

    def _on_any_key_press(self, key) -> None:
        """Handle any key press events - determine if basic or enhanced."""
        if self._is_basic_key_pressed(key):
            self.hotkey_pressed = True
            if not self.is_recording:
                self._start_basic_recording()
        elif self._is_enhanced_key_pressed(key):
            self.hotkey_pressed = True
            if not self.is_recording:
                self._start_enhanced_recording()

    def _on_any_key_release(self, key) -> None:
        """Handle any key release events - determine if basic or enhanced."""
        if self._is_basic_key_pressed(key):
            self.hotkey_pressed = False
            if self.is_recording:
                self._stop_basic_recording_and_process()
        elif self._is_enhanced_key_pressed(key):
            self.hotkey_pressed = False
            if self.is_recording:
                self._stop_enhanced_recording_and_process()

    def _start_basic_recording(self) -> None:
        """Start basic recording with basic sound."""
        if self.is_recording:
            return

        try:
            self.is_recording = True
            self.recording_type = "basic"

            # Create new session
            self.current_session = self.session_manager.create_session()
            self.current_session.state = RecordingState.RECORDING
            self.current_session.start_time = datetime.now()
            
            # Start audio recording
            session_id = self.audio_recorder.start_recording(self.config.audio)
            self.current_session.id = session_id
            
            # Play start beep through audio recorder
            self.audio_recorder.play_start_beep("basic")
            
            # Update session
            self.session_manager.update_session(self.current_session)

            # Recording started notification
            self.console.info(f"Basic recording started (Session: {session_id})")

        except Exception as e:
            self.console.error(f"Error starting basic recording: {e}")

            if self.current_session:
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)

    def _stop_basic_recording_and_process(self) -> None:
        """Stop basic recording and process the audio."""
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
            
            # Play stop beep through audio recorder
            self.audio_recorder.play_stop_beep("basic")
            
            # Stop recording
            audio_file_path = self.audio_recorder.stop_recording(
                self.current_session.id
            )
            if not audio_file_path:
                self.console.warning("No audio file generated")

                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
                return
            # Update session with audio file path
            self.current_session.audio_file_path = audio_file_path
            self.session_manager.update_session(self.current_session)

            # Processing notification
            self.console.info("Basic recording stopped. Transcribing...")

            # Use regular transcription only for basic recording
            transcription_result = self.transcription_service.transcribe(
                audio_file_path
            )
            if transcription_result and transcription_result.text.strip():
                # Update session with transcript
                self.current_session.transcript = transcription_result.text
                self.current_session.state = RecordingState.COMPLETED
                self.session_manager.update_session(self.current_session)

                # Auto-paste if enabled
                if self.config.general.auto_paste:
                    success = self.text_paster.paste_text(transcription_result.text)
                    if success:
                        self.console.info("Basic transcription pasted successfully")
                    else:
                        self.console.warning("Failed to paste basic transcription")

                # Success notification
                self.console.info(
                    f"Basic transcription completed. Text: {transcription_result.text[:100]}..."
                )
            else:
                # No transcription result
                self.console.warning("No transcription generated")

                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)

            # Clean up audio file
            try:
                if os.path.exists(audio_file_path):
                    os.unlink(audio_file_path)
            except Exception as e:
                self.console.warning(f"Failed to clean up audio file: {e}")

        except Exception as e:
            self.console.error(f"Error processing recording: {e}")

            if self.current_session:
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
        finally:
            self.is_recording = False
            self.current_session = None

    def _start_enhanced_recording(self) -> None:
        """Start enhanced recording with GPT post-processing."""
        if self.is_recording:
            return

        try:
            self.is_recording = True
            self.recording_type = "enhanced"

            # Create new session
            self.current_session = self.session_manager.create_session()
            self.current_session.state = RecordingState.RECORDING
            self.current_session.start_time = datetime.now()

            # Start audio recording
            session_id = self.audio_recorder.start_recording(self.config.audio)
            self.current_session.id = session_id

            # Play start beep through audio recorder
            self.audio_recorder.play_start_beep("enhanced")

            # Update session
            self.session_manager.update_session(self.current_session)

            # Enhanced recording started notification
            self.console.info(f"Enhanced recording started (Session: {session_id})")

        except Exception as e:
            self.console.error(f"Error starting enhanced recording: {e}")

            if self.current_session:
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)

    def _stop_enhanced_recording_and_process(self) -> None:
        """Stop enhanced recording and process with LLM enhancement."""
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

            # Play stop beep through audio recorder
            self.audio_recorder.play_stop_beep("enhanced")

            # Stop recording
            audio_file_path = self.audio_recorder.stop_recording(
                self.current_session.id
            )
            if not audio_file_path:
                self.console.warning("No audio file generated")

                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
                return

            # Update session with audio file path
            self.current_session.audio_file_path = audio_file_path
            self.session_manager.update_session(self.current_session)

            # Processing notification
            self.console.info(
                "Enhanced recording stopped. Transcribing and enhancing..."
            )

            # Use enhanced transcription with LLM
            if self.enhanced_transcription_service:
                enhanced_result = (
                    self.enhanced_transcription_service.transcribe_and_enhance(
                        audio_file_path
                    )
                )

                # Update session with enhanced transcript (always use enhanced text only)
                self.current_session.transcript = enhanced_result.enhanced_text

                self.current_session.state = RecordingState.COMPLETED
                self.session_manager.update_session(self.current_session)

                # Auto-paste if enabled
                if self.config.general.auto_paste:
                    text_to_paste = enhanced_result.enhanced_text
                    success = self.text_paster.paste_text(text_to_paste)
                    if success:
                        self.console.info("Enhanced text pasted successfully")
                    else:
                        self.console.warning("Failed to paste enhanced text")

                # Success notification
                self.console.info(
                    f"Enhanced transcription completed. Enhanced text: {enhanced_result.enhanced_text[:100]}..."
                )

            else:
                # Fallback to regular transcription if enhanced service not available
                self.console.warning(
                    "Enhanced transcription service not available, using regular transcription"
                )
                transcription_result = self.transcription_service.transcribe(
                    audio_file_path
                )
                if transcription_result and transcription_result.text.strip():
                    self.current_session.transcript = transcription_result.text
                    self.current_session.state = RecordingState.COMPLETED
                    self.session_manager.update_session(self.current_session)

                    if self.config.general.auto_paste:
                        success = self.text_paster.paste_text(transcription_result.text)
                        if success:
                            self.console.info(
                                "Fallback transcription pasted successfully"
                            )
                        else:
                            self.console.warning(
                                "Failed to paste fallback transcription"
                            )

                    self.console.info(
                        f"Fallback transcription completed. Text: {transcription_result.text[:100]}..."
                    )
                else:
                    self.console.warning("No transcription generated")
                    self.current_session.state = RecordingState.ERROR
                    self.session_manager.update_session(self.current_session)

            # Clean up audio file
            try:
                if os.path.exists(audio_file_path):
                    os.unlink(audio_file_path)
            except Exception as e:
                self.console.warning(f"Failed to clean up audio file: {e}")

        except Exception as e:
            self.console.error(f"Error processing enhanced recording: {e}")

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

    def _stop_recording_and_process(self) -> None:
        """Stop the current recording and process it based on the recording type."""
        if not self.is_recording or not self.current_session:
            return

        # Determine which type of recording is active and call appropriate method
        if hasattr(self, 'recording_type') and self.recording_type == "enhanced":
            self._stop_enhanced_recording_and_process()
        else:
            # Default to basic recording
            self._stop_basic_recording_and_process()

    def get_current_session(self) -> Optional[RecordingSession]:
        """Get the current recording session."""
        return self.current_session

    def get_session_history(self) -> list[RecordingSession]:
        """Get all recording sessions."""
        return self.session_manager.get_all_sessions()
