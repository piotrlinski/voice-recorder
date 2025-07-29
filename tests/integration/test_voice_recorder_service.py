"""
Integration tests for voice recorder service.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from src.voice_recorder.domain.models import ApplicationConfig, RecordingState
from src.voice_recorder.services.voice_recorder_service import VoiceRecorderService


class TestVoiceRecorderService:
    """Integration tests for VoiceRecorderService."""

    def test_service_initialization(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test service initialization with all components."""
        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        assert service.audio_recorder == mock_audio_recorder
        assert service.transcription_service == mock_transcription_service
        assert service.hotkey_listener == mock_hotkey_listener
        assert service.text_paster == mock_text_paster
        assert service.session_manager == mock_session_manager
        assert service.audio_feedback == mock_audio_feedback
        assert service.config == test_config
        assert service.current_session is None
        assert not service.is_recording

    def test_start_service(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test starting the service."""
        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        service.start()

        # is_recording should be False initially (only True when recording)
        assert not service.is_recording
        mock_hotkey_listener.start_listening.assert_called_once()

    def test_stop_service(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test stopping the service."""
        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        service.start()
        service.stop()

        assert not service.is_recording
        mock_hotkey_listener.stop_listening.assert_called_once()

    def test_hotkey_press_detection(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test hotkey press detection."""
        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        service.start()

        # Simulate hotkey press
        mock_key = Mock()
        mock_key.char = None
        mock_key.name = "shift_r"
        mock_key.__str__ = Mock(return_value="Key.shift_r")

        service._on_key_press(mock_key)

        # Verify recording started
        assert service.current_session is not None
        assert service.current_session.state == RecordingState.RECORDING
        mock_audio_feedback.play_start_beep.assert_called_once()

    def test_hotkey_release_detection(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test hotkey release detection."""
        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        service.start()

        # Start recording first
        mock_key = Mock()
        mock_key.char = None
        mock_key.name = "shift_r"
        mock_key.__str__ = Mock(return_value="Key.shift_r")
        service._on_key_press(mock_key)

        # Mock audio recorder to return a file
        mock_audio_recorder.stop_recording.return_value = "test_audio.wav"

        # Simulate hotkey release
        service._on_key_release(mock_key)

        # Verify transcription was called
        mock_transcription_service.transcribe.assert_called_once_with("test_audio.wav")
        mock_audio_feedback.play_stop_beep.assert_called_once()

    def test_full_recording_workflow(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test complete recording workflow."""
        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        service.start()

        # Mock key for hotkey detection
        mock_key = Mock()
        mock_key.char = None
        mock_key.name = "shift_r"
        mock_key.__str__ = Mock(return_value="Key.shift_r")

        # Mock audio recorder
        mock_audio_recorder.start_recording.return_value = "test_session"
        mock_audio_recorder.stop_recording.return_value = "test_audio.wav"

        # Start recording
        service._on_key_press(mock_key)

        # Verify recording started
        assert service.current_session is not None
        assert service.current_session.state == RecordingState.RECORDING
        mock_audio_recorder.start_recording.assert_called_once()
        mock_audio_feedback.play_start_beep.assert_called_once()

        # Stop recording
        service._on_key_release(mock_key)

        # Verify recording stopped and transcription started
        mock_audio_recorder.stop_recording.assert_called_once_with("test_session")
        mock_transcription_service.transcribe.assert_called_once_with("test_audio.wav")
        mock_audio_feedback.play_stop_beep.assert_called_once()

        # Verify session was completed and cleaned up
        assert service.current_session is None
        assert not service.is_recording

    def test_error_handling_during_recording(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test error handling during recording."""
        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        service.start()

        # Mock key
        mock_key = Mock()
        mock_key.char = None
        mock_key.name = "shift_r"
        mock_key.__str__ = Mock(return_value="Key.shift_r")

        # Mock audio recorder to raise an error
        mock_audio_recorder.start_recording.side_effect = Exception("Recording failed")

        # Start recording should handle the error gracefully
        service._on_key_press(mock_key)

        # Verify error state
        assert service.current_session is not None
        assert service.current_session.state == RecordingState.ERROR

    def test_no_transcript_generated(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test handling when no transcript is generated."""
        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        service.start()

        # Mock key
        mock_key = Mock()
        mock_key.char = None
        mock_key.name = "shift_r"
        mock_key.__str__ = Mock(return_value="Key.shift_r")

        # Mock audio recorder
        mock_audio_recorder.start_recording.return_value = "test_session"
        mock_audio_recorder.stop_recording.return_value = "test_audio.wav"

        # Mock transcription service to return None
        mock_transcription_service.transcribe.return_value = None

        # Start and stop recording
        service._on_key_press(mock_key)
        service._on_key_release(mock_key)

        # Verify transcription was called but no text was pasted
        mock_transcription_service.transcribe.assert_called_once()
        mock_text_paster.paste_text.assert_not_called()

    def test_auto_paste_disabled(
        self,
        test_config,
        mock_audio_recorder,
        mock_transcription_service,
        mock_hotkey_listener,
        mock_text_paster,
        mock_session_manager,
        mock_audio_feedback,
        mock_console,
    ):
        """Test behavior when auto-paste is disabled."""
        # Disable auto-paste in config
        test_config.auto_paste = False

        service = VoiceRecorderService(
            audio_recorder=mock_audio_recorder,
            transcription_service=mock_transcription_service,
            hotkey_listener=mock_hotkey_listener,
            text_paster=mock_text_paster,
            session_manager=mock_session_manager,
            audio_feedback=mock_audio_feedback,
            config=test_config,
            console=mock_console,
        )

        service.start()

        # Mock key
        mock_key = Mock()
        mock_key.char = None
        mock_key.name = "shift_r"
        mock_key.__str__ = Mock(return_value="Key.shift_r")

        # Mock audio recorder
        mock_audio_recorder.start_recording.return_value = "test_session"
        mock_audio_recorder.stop_recording.return_value = "test_audio.wav"

        # Start and stop recording
        service._on_key_press(mock_key)
        service._on_key_release(mock_key)

        # Verify transcription was called but no text was pasted
        mock_transcription_service.transcribe.assert_called_once()
        mock_text_paster.paste_text.assert_not_called()
