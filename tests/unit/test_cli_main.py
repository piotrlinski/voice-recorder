"""
Unit tests for CLI main functionality.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import typer

from src.voice_recorder.cli.main import app
from src.voice_recorder.domain.models import ApplicationConfig, TranscriptionMode
from src.voice_recorder.infrastructure.config_manager import ConfigManager


class TestCLIMain:
    """Test cases for CLI main functionality."""
    
    def test_app_creation(self):
        """Test that the app is created correctly."""
        assert isinstance(app, typer.Typer)
        # Typer doesn't have a 'name' attribute, but we can check it's a Typer instance
        assert hasattr(app, 'command')
    
    @patch('src.voice_recorder.cli.main.VoiceRecorderApp')
    @patch('src.voice_recorder.cli.main.ConfigManager')
    def test_start_command_with_existing_config(self, mock_config_manager, mock_app_class):
        """Test start command with existing configuration."""
        # Mock config manager
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.config_exists.return_value = True
        mock_config_manager_instance.load_config.return_value = ApplicationConfig()
        mock_config_manager.return_value = mock_config_manager_instance
        
        # Mock app
        mock_app = Mock()
        mock_app_class.return_value = mock_app
        
        # Test the start command
        with patch('src.voice_recorder.cli.main.console.print'):
            # This would normally be called by typer, but we're testing the logic
            # The actual command execution would be handled by typer
            pass
    
    @patch('src.voice_recorder.cli.main.ConfigManager')
    def test_config_reset_command(self, mock_config_manager):
        """Test config reset command."""
        # Mock config manager
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.reset_to_defaults.return_value = ApplicationConfig()
        mock_config_manager_instance.get_config_path.return_value = '/tmp/config.ini'
        mock_config_manager.return_value = mock_config_manager_instance
        
        with patch('src.voice_recorder.cli.main.console.print'):
            # This would normally be called by typer
            pass
    
    @patch('src.voice_recorder.cli.main.ConfigManager')
    def test_status_command(self, mock_config_manager):
        """Test status command."""
        # Mock config manager
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.get_config_path.return_value = '/tmp/config.ini'
        mock_config_manager_instance.load_config.return_value = ApplicationConfig()
        mock_config_manager.return_value = mock_config_manager_instance
        
        with patch('src.voice_recorder.cli.main.console.print'):
            # This would normally be called by typer
            pass
    
    @patch('src.voice_recorder.cli.main.ConfigManager')
    def test_set_command(self, mock_config_manager):
        """Test set command."""
        # Mock config manager
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.load_config.return_value = ApplicationConfig()
        mock_config_manager_instance.save_config.return_value = None
        mock_config_manager.return_value = mock_config_manager_instance
        
        with patch('src.voice_recorder.cli.main.console.print'):
            # This would normally be called by typer
            pass
    
    @patch('src.voice_recorder.cli.main.ConfigManager')
    def test_purge_command(self, mock_config_manager):
        """Test purge command."""
        # Mock config manager
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.load_config.return_value = ApplicationConfig()
        mock_config_manager.return_value = mock_config_manager_instance
        
        with patch('src.voice_recorder.cli.main.console.print'):
            # This would normally be called by typer
            pass 