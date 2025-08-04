"""
Unit tests for the application module.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from src.voice_recorder.api.app import VoiceRecorderApp, create_app, main
from src.voice_recorder.domain.models import ApplicationConfig


class TestVoiceRecorderApp:
    """Test cases for VoiceRecorderApp."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory")
    def test_init_with_config(self, mock_factory_class):
        """Test VoiceRecorderApp initialization with config."""
        mock_service = Mock()
        mock_enhanced_service = Mock()
        mock_factory_instance = Mock()
        mock_factory_instance.create_service.return_value = mock_service
        mock_factory_instance.create_enhanced_service.return_value = mock_enhanced_service
        mock_factory_class.return_value = mock_factory_instance

        # Create config with valid API key
        from src.voice_recorder.domain.models import (
            TranscriptionConfig, TranscriptionMode, OpenAITranscriptionConfig
        )
        
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(api_key="test-key")
        )
        config = ApplicationConfig(transcription=transcription_config)
        app = VoiceRecorderApp(config)
        assert app.config == config

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_enhanced_service"
    )
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_service"
    )
    @patch("src.voice_recorder.infrastructure.config_manager.ConfigManager.load_config")
    def test_init_without_config(self, mock_load_config, mock_create_service, mock_create_enhanced_service):
        """Test VoiceRecorderApp initialization without config."""
        mock_service = Mock()
        mock_enhanced_service = Mock()
        mock_create_service.return_value = mock_service
        mock_create_enhanced_service.return_value = mock_enhanced_service
        
        # Mock config loading to return a valid config
        from src.voice_recorder.domain.models import (
            TranscriptionConfig, TranscriptionMode, OpenAITranscriptionConfig
        )
        
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(api_key="test-key")
        )
        mock_config = ApplicationConfig(transcription=transcription_config)
        mock_load_config.return_value = mock_config

        app = VoiceRecorderApp()
        assert isinstance(app.config, ApplicationConfig)

    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_enhanced_service"
    )
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_service"
    )
    @patch("src.voice_recorder.infrastructure.config_manager.ConfigManager.load_config")
    def test_init_without_api_key(self, mock_load_config, mock_create_service, mock_create_enhanced_service):
        """Test VoiceRecorderApp initialization without API key."""
        mock_service = Mock()
        mock_enhanced_service = Mock()
        mock_create_service.return_value = mock_service
        mock_create_enhanced_service.return_value = mock_enhanced_service

        # Mock config loading to return a local config (no API key needed)
        from src.voice_recorder.domain.models import (
            TranscriptionConfig, TranscriptionMode, LocalTranscriptionConfig
        )
        
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode.LOCAL,
            local=LocalTranscriptionConfig(whisper_model="small")
        )
        mock_config = ApplicationConfig(transcription=transcription_config)
        mock_load_config.return_value = mock_config

        with patch.dict(os.environ, {}, clear=True):
            # The app should still initialize even without API key
            # since it uses the factory pattern now
            app = VoiceRecorderApp()
            assert isinstance(app.config, ApplicationConfig)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_enhanced_service"
    )
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_service"
    )
    @patch("src.voice_recorder.infrastructure.config_manager.ConfigManager.load_config")
    def test_signal_handler(self, mock_load_config, mock_create_service, mock_create_enhanced_service):
        """Test signal handler."""
        mock_service = Mock()
        mock_enhanced_service = Mock()
        mock_create_service.return_value = mock_service
        mock_create_enhanced_service.return_value = mock_enhanced_service
        
        # Mock config loading
        from src.voice_recorder.domain.models import (
            TranscriptionConfig, TranscriptionMode, OpenAITranscriptionConfig
        )
        
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(api_key="test-key")
        )
        mock_config = ApplicationConfig(transcription=transcription_config)
        mock_load_config.return_value = mock_config

        app = VoiceRecorderApp()
        with patch.object(app, "stop") as mock_stop:
            with patch("sys.exit") as mock_exit:
                app._signal_handler(None, None)
                mock_stop.assert_called_once()
                mock_exit.assert_called_once_with(0)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_enhanced_service"
    )
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_service"
    )
    @patch("src.voice_recorder.infrastructure.config_manager.ConfigManager.load_config")
    def test_start_and_stop(self, mock_load_config, mock_create_service, mock_create_enhanced_service):
        """Test start and stop methods."""
        mock_service = Mock()
        mock_enhanced_service = Mock()
        mock_create_service.return_value = mock_service
        mock_create_enhanced_service.return_value = mock_enhanced_service
        
        # Mock config loading
        from src.voice_recorder.domain.models import (
            TranscriptionConfig, TranscriptionMode, OpenAITranscriptionConfig
        )
        
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(api_key="test-key")
        )
        mock_config = ApplicationConfig(transcription=transcription_config)
        mock_load_config.return_value = mock_config

        app = VoiceRecorderApp()

        # Mock the voice recorder service
        mock_service = Mock()
        app.voice_recorder_service = mock_service

        # Test start
        with patch("time.sleep", side_effect=KeyboardInterrupt):
            app.start()
            mock_service.start.assert_called_once()

        # Test stop
        app.stop()
        mock_service.stop.assert_called_once()


class TestCreateApp:
    """Test cases for create_app function."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_enhanced_service"
    )
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_service"
    )
    def test_create_app_with_config(self, mock_create_service, mock_create_enhanced_service):
        """Test create_app with config."""
        mock_service = Mock()
        mock_enhanced_service = Mock()
        mock_create_service.return_value = mock_service
        mock_create_enhanced_service.return_value = mock_enhanced_service

        # Create config with valid API key
        from src.voice_recorder.domain.models import (
            TranscriptionConfig, TranscriptionMode, OpenAITranscriptionConfig
        )
        
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(api_key="test-key")
        )
        config = ApplicationConfig(transcription=transcription_config)
        app = create_app(config)
        assert isinstance(app, VoiceRecorderApp)
        assert app.config == config

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_enhanced_service"
    )
    @patch(
        "src.voice_recorder.infrastructure.transcription.simple_factory.SimpleTranscriptionServiceFactory.create_service"
    )
    @patch("src.voice_recorder.infrastructure.config_manager.ConfigManager.load_config")
    def test_create_app_without_config(self, mock_load_config, mock_create_service, mock_create_enhanced_service):
        """Test create_app without config."""
        mock_service = Mock()
        mock_enhanced_service = Mock()
        mock_create_service.return_value = mock_service
        mock_create_enhanced_service.return_value = mock_enhanced_service
        
        # Mock config loading
        from src.voice_recorder.domain.models import (
            TranscriptionConfig, TranscriptionMode, OpenAITranscriptionConfig
        )
        
        transcription_config = TranscriptionConfig(
            mode=TranscriptionMode.OPENAI,
            openai=OpenAITranscriptionConfig(api_key="test-key")
        )
        mock_config = ApplicationConfig(transcription=transcription_config)
        mock_load_config.return_value = mock_config

        app = create_app()
        assert isinstance(app, VoiceRecorderApp)
        assert isinstance(app.config, ApplicationConfig)


class TestMain:
    """Test cases for main function."""

    @patch("src.voice_recorder.cli.commands.main")
    def test_main(self, mock_cli_main):
        """Test main function."""
        mock_cli_main.return_value = 0

        with patch("sys.exit") as mock_exit:
            main()
            mock_cli_main.assert_called_once()
            mock_exit.assert_called_once_with(0)
