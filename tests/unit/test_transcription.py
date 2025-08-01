"""
Unit tests for transcription services.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from src.voice_recorder.domain.models import (
    TranscriptionConfig,
    TranscriptionMode,
    TranscriptionResult,
)
from src.voice_recorder.infrastructure.transcription import OpenAITranscriptionService


class MockTranscriptionService:
    """Mock transcription service for testing."""

    def __init__(self, mock_text: str = "Test transcription"):
        self.mock_text = mock_text

    def transcribe(self, audio_file_path: str):
        """Mock transcription method."""
        from src.voice_recorder.domain.models import TranscriptionResult

        return TranscriptionResult(text=self.mock_text, confidence=0.95, duration=1.0)


class TestMockTranscriptionService:
    """Test cases for MockTranscriptionService."""

    def test_init(self):
        """Test MockTranscriptionService initialization."""
        service = MockTranscriptionService("Test text")
        assert service.mock_text == "Test text"

    def test_transcribe(self):
        """Test MockTranscriptionService transcribe method."""
        service = MockTranscriptionService("Test transcription")
        result = service.transcribe("dummy_file.wav")

        assert isinstance(result, TranscriptionResult)
        assert result.text == "Test transcription"
        assert result.confidence == 0.95

        assert result.duration == 1.0


class TestOpenAITranscriptionService:
    """Test cases for OpenAITranscriptionService."""

    def test_init_without_openai(self):
        """Test initialization when OpenAI is not available."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER,
            model_name="whisper-1",
            api_key="test_key",
        )
        with patch("builtins.__import__", side_effect=ImportError):
            with pytest.raises(RuntimeError, match="OpenAI library not available"):
                OpenAITranscriptionService(config)

    def test_init_with_openai(self):
        """Test initialization when OpenAI is available."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER,
            model_name="whisper-1",
            api_key="test_key",
        )
        mock_openai = Mock()
        mock_openai.api_key = None

        with patch("builtins.__import__", return_value=mock_openai):
            service = OpenAITranscriptionService(config)
            assert service.config.api_key == "test_key"

    def test_transcribe_file_not_found(self):
        """Test transcribe with non-existent file."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER,
            model_name="whisper-1",
            api_key="test_key",
        )
        mock_openai = Mock()

        with patch("builtins.__import__", return_value=mock_openai):
            service = OpenAITranscriptionService(config)

            with pytest.raises(FileNotFoundError):
                service.transcribe("non_existent_file.wav")

    def test_transcribe_success(self):
        """Test successful transcription."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER,
            model_name="whisper-1",
            api_key="test_key",
        )
        mock_openai = Mock()
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client

        # Mock the transcription response
        mock_response = Mock()
        mock_response.text = "Hello world"
        mock_client.audio.transcriptions.create.return_value = mock_response

        with patch("builtins.__import__", return_value=mock_openai):
            service = OpenAITranscriptionService(config)

            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_file = f.name
                f.write(b"test_audio_data")

            try:
                result = service.transcribe(temp_file)

                assert isinstance(result, TranscriptionResult)
                assert result.text == "Hello world"
                assert result.confidence is None
                assert result.duration is None

                # Verify OpenAI was called correctly
                mock_client.audio.transcriptions.create.assert_called_once()
                call_args = mock_client.audio.transcriptions.create.call_args
                assert call_args[1]["model"] == "whisper-1"

            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

    def test_transcribe_openai_error(self):
        """Test transcription with OpenAI error."""
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI_WHISPER,
            model_name="whisper-1",
            api_key="test_key",
        )
        mock_openai = Mock()
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client

        # Mock OpenAI error
        mock_client.audio.transcriptions.create.side_effect = Exception("OpenAI error")

        with patch("builtins.__import__", return_value=mock_openai):
            service = OpenAITranscriptionService(config)

            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_file = f.name
                f.write(b"test_audio_data")

            try:
                with pytest.raises(
                    RuntimeError, match="OpenAI transcription failed: OpenAI error"
                ):
                    service.transcribe(temp_file)
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

    def test_transcribe_without_client(self):
        """Test transcribe when client is not initialized."""
        # This test is no longer applicable since we don't store a client instance
        # The new implementation imports openai directly in the transcribe method
        pass
