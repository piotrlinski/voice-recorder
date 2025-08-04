"""
Pytest configuration and shared fixtures.
"""

import os
import tempfile
from typing import Generator
from unittest.mock import Mock

import pytest

from src.voice_recorder.domain.models import (
    ApplicationConfig,
    AudioConfig,
    ControlsConfig,
    TranscriptionResult,
)


@pytest.fixture
def test_config() -> ApplicationConfig:
    """Provide a test application configuration."""
    return ApplicationConfig(
        controls=ControlsConfig(basic_key="shift_r", enhanced_key="ctrl_l"),
        audio=AudioConfig(sample_rate=16000, channels=1),
    )


@pytest.fixture
def mock_audio_recorder() -> Mock:
    """Provide a mock audio recorder."""
    mock = Mock()
    mock.start_recording.return_value = "test_session"
    mock.stop_recording.return_value = "test_audio.wav"
    mock.is_recording.return_value = False
    return mock


@pytest.fixture
def mock_transcription_service() -> Mock:
    """Provide a mock transcription service."""
    mock = Mock()
    mock_result = TranscriptionResult(
        text="Test transcription result", confidence=0.95, duration=1.0
    )
    mock.transcribe.return_value = mock_result
    return mock


@pytest.fixture
def mock_hotkey_listener() -> Mock:
    """Provide a mock hotkey listener."""
    mock = Mock()
    mock.start_listening = Mock()
    mock.stop_listening = Mock()
    return mock


@pytest.fixture
def mock_text_paster() -> Mock:
    """Provide a mock text paster."""
    mock = Mock()
    mock.paste_text = Mock()
    return mock


@pytest.fixture
def mock_session_manager() -> Mock:
    """Provide a mock session manager."""
    from datetime import datetime
    from src.voice_recorder.domain.models import RecordingSession

    mock = Mock()
    mock_session = RecordingSession(id="test_session", start_time=datetime.now())
    mock.create_session = Mock(return_value=mock_session)
    mock.update_session = Mock()
    mock.get_session = Mock()
    return mock




@pytest.fixture
def mock_console() -> Mock:
    """Provide a mock console interface."""
    mock = Mock()
    # Mock all the ConsoleInterface methods
    mock.info = Mock()
    mock.error = Mock()
    mock.warning = Mock()
    mock.debug = Mock()
    return mock


@pytest.fixture
def temp_audio_file() -> Generator[str, None, None]:
    """Provide a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_file = f.name

    yield temp_file

    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def sample_audio_data() -> bytes:
    """Provide sample audio data for testing."""
    # Create a simple 1-second 16kHz mono WAV file
    import tempfile
    import wave

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_file = f.name

    try:
        with wave.open(temp_file, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(16000)
            # Generate 1 second of silence
            wf.writeframes(b"\x00\x00" * 16000)

        with open(temp_file, "rb") as f:
            data = f.read()

        return data
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
