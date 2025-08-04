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
from src.voice_recorder.infrastructure.transcription.providers import OpenAITranscriptionProvider
from src.voice_recorder.infrastructure.transcription import SimpleTranscriptionService
from src.voice_recorder.infrastructure.transcription.simple_factory import SimpleTranscriptionServiceFactory


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


class TestOpenAITranscriptionProvider:
    """Test cases for the new OpenAITranscriptionProvider."""

    def test_init(self):
        """Test initialization."""
        from src.voice_recorder.domain.models import OpenAITranscriptionConfig
        
        config = OpenAITranscriptionConfig(
            api_key="test_key",
            whisper_model="whisper-1",
        )
        provider = OpenAITranscriptionProvider(config)
        assert provider.config.api_key == "test_key"
        assert provider.config.whisper_model == "whisper-1"

    def test_transcribe_file_not_found(self):
        """Test transcribe with non-existent file."""
        from src.voice_recorder.domain.models import OpenAITranscriptionConfig
        
        config = OpenAITranscriptionConfig(
            api_key="test_key",
            whisper_model="whisper-1",
        )
        provider = OpenAITranscriptionProvider(config)
        
        with pytest.raises(FileNotFoundError):
            provider.transcribe("non_existent_file.wav")

    def test_transcribe_success(self):
        """Test successful transcription."""
        from src.voice_recorder.domain.models import OpenAITranscriptionConfig
        
        config = OpenAITranscriptionConfig(
            api_key="test_key",
            whisper_model="whisper-1",
        )
        
        # Mock the openai import in the provider's __init__ method
        with patch('builtins.__import__') as mock_import:
            # Setup mock for openai import
            mock_openai = Mock()
            mock_client = Mock()
            mock_openai.OpenAI.return_value = mock_client
            
            # Save the original import function
            original_import = __import__
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'openai':
                    return mock_openai
                return original_import(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            provider = OpenAITranscriptionProvider(config)
            
            # Now mock the response for transcription
            mock_response = Mock()
            mock_response.text = "Hello world"
            mock_client.audio.transcriptions.create.return_value = mock_response
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_file = f.name
                f.write(b"test_audio_data")
            
            try:
                result = provider.transcribe(temp_file)
                
                assert hasattr(result, 'text')
                assert result.text == "Hello world"
                
                # Verify OpenAI was called correctly
                mock_client.audio.transcriptions.create.assert_called_once()
                call_args = mock_client.audio.transcriptions.create.call_args
                assert call_args[1]["model"] == "whisper-1"
            
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

    def test_transcribe_openai_error(self):
        """Test transcription with OpenAI error."""
        from src.voice_recorder.domain.models import OpenAITranscriptionConfig
        
        config = OpenAITranscriptionConfig(
            api_key="test_key",
            whisper_model="whisper-1",
        )
        
        # Mock the openai import and client to raise an error
        with patch('builtins.__import__') as mock_import:
            # Setup mock for openai import
            mock_openai = Mock()
            mock_client = Mock()
            mock_openai.OpenAI.return_value = mock_client
            mock_client.audio.transcriptions.create.side_effect = Exception("OpenAI error")
            
            # Save the original import function
            original_import = __import__
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'openai':
                    return mock_openai
                return original_import(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            provider = OpenAITranscriptionProvider(config)
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_file = f.name
                f.write(b"test_audio_data")
            
            try:
                with pytest.raises(RuntimeError, match="OpenAI transcription failed"):
                    provider.transcribe(temp_file)
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)


class TestSimpleTranscriptionService:
    """Test cases for SimpleTranscriptionService."""
    
    def test_init(self):
        """Test service initialization."""
        mock_provider = Mock()
        mock_processor = Mock()
        mock_console = Mock()
        
        service = SimpleTranscriptionService(mock_provider, mock_processor, mock_console)
        assert service.transcription_provider == mock_provider
        assert service.text_processor == mock_processor
        assert service.console == mock_console
    
    def test_transcribe_success(self):
        """Test successful transcription."""
        mock_provider = Mock()
        mock_result = TranscriptionResult(text="Hello world", confidence=0.95, duration=1.0)
        mock_provider.transcribe.return_value = mock_result
        
        service = SimpleTranscriptionService(mock_provider)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name
            f.write(b"test_audio_data")
        
        try:
            result = service.transcribe(temp_file)
            assert result.text == "Hello world"
            mock_provider.transcribe.assert_called_once_with(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_transcribe_file_not_found(self):
        """Test transcription with non-existent file."""
        mock_provider = Mock()
        service = SimpleTranscriptionService(mock_provider)
        
        with pytest.raises(FileNotFoundError):
            service.transcribe("non_existent_file.wav")
    
    def test_transcribe_and_enhance_with_processor(self):
        """Test transcription with text enhancement."""
        mock_provider = Mock()
        mock_processor = Mock()
        mock_console = Mock()
        
        # Mock the transcription result
        mock_result = TranscriptionResult(text="Hello world", confidence=0.95, duration=1.0)
        mock_provider.transcribe.return_value = mock_result
        
        # Mock text processor
        mock_processor.is_available.return_value = True
        mock_processor.process_text.return_value = "Hello, world! This is improved."
        
        service = SimpleTranscriptionService(mock_provider, mock_processor, mock_console)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name
            f.write(b"test_audio_data")
        
        try:
            result = service.transcribe_and_enhance(temp_file)
            assert result.text == "Hello, world! This is improved."
            mock_processor.process_text.assert_called_once_with("Hello world")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_transcribe_and_enhance_without_processor(self):
        """Test transcription without text processor."""
        mock_provider = Mock()
        mock_result = TranscriptionResult(text="Hello world", confidence=0.95, duration=1.0)
        mock_provider.transcribe.return_value = mock_result
        
        service = SimpleTranscriptionService(mock_provider)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name
            f.write(b"test_audio_data")
        
        try:
            result = service.transcribe_and_enhance(temp_file)
            assert result.text == "Hello world"
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestSimpleTranscriptionServiceFactory:
    """Test cases for SimpleTranscriptionServiceFactory."""
    
    def test_create_service_openai(self):
        """Test creating OpenAI service."""
        from src.voice_recorder.domain.models import (
            TranscriptionConfig,
            TranscriptionMode,
            OpenAITranscriptionConfig
        )
        
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(api_key="test-key")
        )
        
        factory = SimpleTranscriptionServiceFactory()
        service = factory.create_service(config)
        
        assert isinstance(service, SimpleTranscriptionService)
        assert service.transcription_provider is not None
    
    def test_create_enhanced_service_openai(self):
        """Test creating enhanced OpenAI service."""
        from src.voice_recorder.domain.models import (
            TranscriptionConfig,
            TranscriptionMode,
            OpenAITranscriptionConfig
        )
        
        config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(api_key="test-key")
        )
        
        factory = SimpleTranscriptionServiceFactory()
        service = factory.create_enhanced_service(config)
        
        assert isinstance(service, SimpleTranscriptionService)
        assert service.transcription_provider is not None
        assert service.text_processor is not None
