"""
Voice recorder service implementation.

This module contains the main service class that orchestrates all voice recording
functionality including audio recording, transcription, and text processing.
"""

import os
import threading
from datetime import datetime
from typing import Optional


from ..domain.interfaces import (
    AudioRecorderInterface,
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
)


class VoiceRecorderService:
    """Main voice recorder service orchestrating all components.

    This service coordinates between audio recording, transcription, hotkey detection,
    text pasting, and session management to provide a complete voice recording solution.

    The service supports two transcription modes:
    - Basic: Direct speech-to-text transcription
    - Enhanced: Speech-to-text with AI-powered text improvement

    Attributes:
        audio_recorder: Interface for audio recording functionality
        transcription_service: Basic transcription service
        enhanced_transcription_service: Enhanced transcription with AI improvement
        hotkey_listener: Hotkey detection and event handling
        text_paster: Text insertion functionality
        session_manager: Recording session management
        config: Application configuration
        console: Logging and console output interface
        current_session: Currently active recording session
        is_recording: Whether a recording is currently in progress
        hotkey_pressed: Whether a hotkey is currently pressed
        recording_type: Type of recording ('basic' or 'enhanced')

    Example:
        >>> from voice_recorder.services.voice_recorder_service import VoiceRecorderService
        >>> from voice_recorder.domain.models import ApplicationConfig
        >>>
        >>> # Initialize with dependency injection
        >>> service = VoiceRecorderService(
        ...     audio_recorder=audio_recorder,
        ...     transcription_service=transcription_service,
        ...     hotkey_listener=hotkey_listener,
        ...     text_paster=text_paster,
        ...     session_manager=session_manager,
        ...     config=config,
        ...     console=console
        ... )
        >>>
        >>> # Start the service
        >>> service.start()
        >>> # Service will now listen for hotkey events
    """

    @staticmethod
    def _is_meaningful_transcription(text: str) -> bool:
        """Check if transcription text contains meaningful content.

        Args:
            text: The transcription text to validate

        Returns:
            True if the text contains meaningful content, False otherwise
        """
        if not text or not text.strip():
            return False

        # Clean the text
        cleaned_text = text.strip().lower()

        # Check minimum length (at least 2 characters)
        if len(cleaned_text) < 2:
            return False

        # Common empty/meaningless transcriptions from Whisper
        meaningless_phrases = {
            "thank you",
            "thanks",
            "bye",
            "goodbye",
            "hello",
            "hi",
            "hey",
            "um",
            "uh",
            "hmm",
            "ah",
            "oh",
            "okay",
            "ok",
            "yes",
            "no",
            "you",
            "the",
            "and",
            "a",
            "an",
            "to",
            "of",
            "in",
            "it",
            "is",
            ".",
            ",",
            "?",
            "!",
            "-",
            "--",
            "...",
            " ",
            "thank you for watching",
            "thank you for listening",
            "music",
            "applause",
            "laughter",
            "silence",
            "noise",
            "[music]",
            "[applause]",
            "[laughter]",
            "[silence]",
            "[noise]",
            "(music)",
            "(applause)",
            "(laughter)",
            "(silence)",
            "(noise)",
        }

        # Remove punctuation and extra spaces for comparison
        import re

        text_for_comparison = re.sub(r"[^\w\s]", "", cleaned_text).strip()

        # If after removing punctuation there's nothing left, it's not meaningful
        if not text_for_comparison:
            return False

        # Check if it's just meaningless phrases
        if text_for_comparison in meaningless_phrases:
            return False

        # Check if it's just single characters or very short words
        words = text_for_comparison.split()
        if len(words) == 1 and len(words[0]) <= 2:
            return False

        # If we get here, it's likely meaningful content
        return True

    def __init__(
        self,
        audio_recorder: AudioRecorderInterface,
        transcription_service: TranscriptionServiceInterface,
        hotkey_listener: HotkeyListenerInterface,
        text_paster: TextPasterInterface,
        session_manager: SessionManagerInterface,
        config: ApplicationConfig,
        console: ConsoleInterface,
        enhanced_transcription_service: (
            EnhancedTranscriptionServiceInterface | None
        ) = None,
    ):
        """Initialize the voice recorder service.

        Args:
            audio_recorder: Audio recording interface implementation
            transcription_service: Basic transcription service for speech-to-text
            hotkey_listener: Hotkey detection and event handling service
            text_paster: Text insertion service for auto-paste functionality
            session_manager: Recording session management service
            config: Application configuration with transcription and control settings
            console: Logging and console output interface
            enhanced_transcription_service: Optional enhanced transcription service
                that provides AI-powered text improvement capabilities

        Note:
            All dependencies are injected following dependency inversion principle.
            The service will operate in basic mode only if enhanced_transcription_service
            is None.
        """
        self.audio_recorder = audio_recorder
        self.transcription_service = transcription_service
        self.enhanced_transcription_service = enhanced_transcription_service
        self.hotkey_listener = hotkey_listener
        self.text_paster = text_paster
        self.session_manager = session_manager
        self.config = config
        self.console = console

        self.current_session: Optional[RecordingSession] = None
        self.is_recording = False
        self.hotkey_pressed = False
        self.recording_type = "basic"  # Track whether recording is basic or enhanced

        # Threading for async processing
        self._processing_thread: Optional[threading.Thread] = None
        self._processing_lock = threading.Lock()

    def start(self) -> None:
        """Start the voice recorder service.

        Initializes hotkey listeners and begins monitoring for recording events.
        The service will listen for both basic and enhanced transcription hotkeys
        as configured in the application config.

        Raises:
            RuntimeError: If the hotkey listener fails to start or initialize

        Note:
            This method is non-blocking. The service runs in the background
            and processes hotkey events asynchronously.
        """
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
        """Stop the voice recorder service.

        Gracefully shuts down the service by:
        1. Stopping any active recording
        2. Waiting for transcription processing to complete
        3. Stopping the hotkey listener

        The method will wait up to 10 seconds for active transcription
        processing to complete before forcing shutdown.

        Note:
            This method is blocking and will wait for clean shutdown.
            Any active recording will be properly saved and processed.
        """
        try:
            if self.is_recording:
                self._stop_current_recording()

            # Wait for any ongoing processing to complete
            with self._processing_lock:
                if self._processing_thread and self._processing_thread.is_alive():
                    self.console.info(
                        "Waiting for transcription processing to complete..."
                    )
                    # Release lock to allow processing to finish
                    pass

            # Wait for thread to complete (with timeout)
            if self._processing_thread and self._processing_thread.is_alive():
                self._processing_thread.join(timeout=10.0)  # Wait up to 10 seconds
                if self._processing_thread.is_alive():
                    self.console.warning(
                        "Transcription processing did not complete within timeout"
                    )

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
        """Start basic recording."""
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
        """Stop basic recording and start async processing."""
        if (
            not self.current_session
            or self.current_session.state != RecordingState.RECORDING
        ):
            return

        try:
            # Update session state immediately
            self.current_session.state = RecordingState.PROCESSING
            self.current_session.end_time = datetime.now()
            self.session_manager.update_session(self.current_session)

            # Stop recording
            audio_file_path = self.audio_recorder.stop_recording(
                self.current_session.id
            )
            if not audio_file_path:
                self.console.warning("No audio file generated")
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
                # Reset recording state to allow new recordings
                self.is_recording = False
                self.current_session = None
                return

            # Update session with audio file path
            self.current_session.audio_file_path = audio_file_path
            self.session_manager.update_session(self.current_session)

            # Start async processing immediately
            self.console.info("Basic recording stopped. Starting transcription...")

            # Launch processing in background thread
            with self._processing_lock:
                if self._processing_thread and self._processing_thread.is_alive():
                    self.console.warning("Another processing operation is in progress")
                    return

                self._processing_thread = threading.Thread(
                    target=self._process_basic_transcription_async,
                    args=(audio_file_path, self.current_session.id),
                    daemon=True,
                )
                self._processing_thread.start()

        except Exception as e:
            self.console.error(f"Error stopping basic recording: {e}")
            if self.current_session:
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
            # Reset recording state to allow new recordings
            self.is_recording = False
            self.current_session = None

    def _process_basic_transcription_async(
        self, audio_file_path: str, session_id: str
    ) -> None:
        """Process basic transcription in background thread."""
        try:
            # Use regular transcription only for basic recording
            transcription_result = self.transcription_service.transcribe(
                audio_file_path
            )

            # Update session in thread-safe manner
            with self._processing_lock:
                session = self.session_manager.get_session(session_id)
                if not session:
                    self.console.warning(
                        f"Session {session_id} not found during processing"
                    )
                    return

                if transcription_result and transcription_result.text.strip():
                    # Check if the transcription contains meaningful content
                    if self._is_meaningful_transcription(transcription_result.text):
                        # Update session with transcript
                        session.transcript = transcription_result.text
                        session.state = RecordingState.COMPLETED
                        self.session_manager.update_session(session)

                        # Auto-paste if enabled
                        if self.config.general.auto_paste:
                            success = self.text_paster.paste_text(
                                transcription_result.text
                            )
                            if success:
                                self.console.info(
                                    "Basic transcription pasted successfully"
                                )
                            else:
                                self.console.warning(
                                    "Failed to paste basic transcription"
                                )

                        # Success notification
                        self.console.info(
                            f"Basic transcription completed. Text: {transcription_result.text[:100]}..."
                        )
                    else:
                        # Transcription exists but is not meaningful - don't paste
                        self.console.info(
                            f"Basic transcription contained no meaningful content: '{transcription_result.text}' - skipping paste"
                        )
                        session.transcript = "[No meaningful content detected]"
                        session.state = RecordingState.COMPLETED
                        self.session_manager.update_session(session)
                else:
                    # No transcription result
                    self.console.warning("No transcription generated")
                    session.state = RecordingState.ERROR
                    self.session_manager.update_session(session)

        except Exception as e:
            self.console.error(f"Error processing basic transcription: {e}")
            # Update session state to error in thread-safe manner
            with self._processing_lock:
                session = self.session_manager.get_session(session_id)
                if session:
                    session.state = RecordingState.ERROR
                    self.session_manager.update_session(session)
        finally:
            # Clean up audio file
            try:
                if os.path.exists(audio_file_path):
                    os.unlink(audio_file_path)
            except Exception as e:
                self.console.warning(f"Failed to clean up audio file: {e}")

            # Reset recording state - keep session for debugging
            with self._processing_lock:
                self.is_recording = False
                # Don't clear current_session to avoid race conditions

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
        """Stop enhanced recording and start async processing."""
        if (
            not self.current_session
            or self.current_session.state != RecordingState.RECORDING
        ):
            return

        try:
            # Update session state immediately
            self.current_session.state = RecordingState.PROCESSING
            self.current_session.end_time = datetime.now()
            self.session_manager.update_session(self.current_session)

            # Stop recording
            audio_file_path = self.audio_recorder.stop_recording(
                self.current_session.id
            )
            if not audio_file_path:
                self.console.warning("No audio file generated")
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
                # Reset recording state to allow new recordings
                self.is_recording = False
                self.current_session = None
                return

            # Update session with audio file path
            self.current_session.audio_file_path = audio_file_path
            self.session_manager.update_session(self.current_session)

            # Start async processing immediately
            self.console.info(
                "Enhanced recording stopped. Starting transcription and enhancement..."
            )

            # Launch processing in background thread
            with self._processing_lock:
                if self._processing_thread and self._processing_thread.is_alive():
                    self.console.warning("Another processing operation is in progress")
                    return

                self._processing_thread = threading.Thread(
                    target=self._process_enhanced_transcription_async,
                    args=(audio_file_path, self.current_session.id),
                    daemon=True,
                )
                self._processing_thread.start()

        except Exception as e:
            self.console.error(f"Error stopping enhanced recording: {e}")
            if self.current_session:
                self.current_session.state = RecordingState.ERROR
                self.session_manager.update_session(self.current_session)
            # Reset recording state to allow new recordings
            self.is_recording = False
            self.current_session = None

    def _process_enhanced_transcription_async(
        self, audio_file_path: str, session_id: str
    ) -> None:
        """Process enhanced transcription in background thread."""
        try:
            # Use enhanced transcription with LLM
            if self.enhanced_transcription_service:
                enhanced_result = (
                    self.enhanced_transcription_service.transcribe_and_enhance(
                        audio_file_path
                    )
                )

                # Update session in thread-safe manner
                with self._processing_lock:
                    session = self.session_manager.get_session(session_id)
                    if not session:
                        self.console.warning(
                            f"Session {session_id} not found during enhanced processing"
                        )
                        return

                    # Check if the enhanced transcription contains meaningful content
                    # Note: enhanced_result is a TranscriptionResult, not EnhancedTranscriptionResult
                    if self._is_meaningful_transcription(enhanced_result.text):
                        # Update session with enhanced transcript
                        session.transcript = enhanced_result.text
                        session.state = RecordingState.COMPLETED
                        self.session_manager.update_session(session)

                        # Auto-paste if enabled
                        if self.config.general.auto_paste:
                            text_to_paste = enhanced_result.text
                            success = self.text_paster.paste_text(text_to_paste)
                            if success:
                                self.console.info("Enhanced text pasted successfully")
                            else:
                                self.console.warning("Failed to paste enhanced text")

                        # Success notification
                        self.console.info(
                            f"Enhanced transcription completed. Enhanced text: {enhanced_result.text[:100]}..."
                        )
                    else:
                        # Enhanced transcription exists but is not meaningful - don't paste
                        self.console.info(
                            f"Enhanced transcription contained no meaningful content: '{enhanced_result.text}' - skipping paste"
                        )
                        session.transcript = "[No meaningful content detected]"
                        session.state = RecordingState.COMPLETED
                        self.session_manager.update_session(session)

            else:
                # Fallback to regular transcription if enhanced service not available
                self.console.warning(
                    "Enhanced transcription service not available, using regular transcription"
                )
                transcription_result = self.transcription_service.transcribe(
                    audio_file_path
                )

                # Update session in thread-safe manner
                with self._processing_lock:
                    session = self.session_manager.get_session(session_id)
                    if not session:
                        self.console.warning(
                            f"Session {session_id} not found during fallback processing"
                        )
                        return

                    if transcription_result and transcription_result.text.strip():
                        # Check if the fallback transcription contains meaningful content
                        if self._is_meaningful_transcription(transcription_result.text):
                            session.transcript = transcription_result.text
                            session.state = RecordingState.COMPLETED
                            self.session_manager.update_session(session)

                            if self.config.general.auto_paste:
                                success = self.text_paster.paste_text(
                                    transcription_result.text
                                )
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
                            # Fallback transcription exists but is not meaningful - don't paste
                            self.console.info(
                                f"Fallback transcription contained no meaningful content: '{transcription_result.text}' - skipping paste"
                            )
                            session.transcript = "[No meaningful content detected]"
                            session.state = RecordingState.COMPLETED
                            self.session_manager.update_session(session)
                    else:
                        self.console.warning("No transcription generated")
                        session.state = RecordingState.ERROR
                        self.session_manager.update_session(session)

        except Exception as e:
            self.console.error(f"Error processing enhanced transcription: {e}")
            # Update session state to error in thread-safe manner
            with self._processing_lock:
                session = self.session_manager.get_session(session_id)
                if session:
                    session.state = RecordingState.ERROR
                    self.session_manager.update_session(session)
        finally:
            # Clean up audio file
            try:
                if os.path.exists(audio_file_path):
                    os.unlink(audio_file_path)
            except Exception as e:
                self.console.warning(f"Failed to clean up audio file: {e}")

            # Reset recording state - keep session for debugging
            with self._processing_lock:
                self.is_recording = False
                # Don't clear current_session to avoid race conditions

    def _stop_current_recording(self) -> None:
        """Stop the current recording if active."""
        if self.is_recording and self.current_session:
            self._stop_recording_and_process()

    def _stop_recording_and_process(self) -> None:
        """Stop the current recording and process it based on the recording type."""
        if not self.is_recording or not self.current_session:
            return

        # Determine which type of recording is active and call appropriate method
        if hasattr(self, "recording_type") and self.recording_type == "enhanced":
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
