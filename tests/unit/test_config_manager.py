"""
Unit tests for configuration manager.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.voice_recorder.domain.models import ApplicationConfig, TranscriptionMode
from src.voice_recorder.infrastructure.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    def test_init_default_config_dir(self):
        """Test initialization with default config directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(temp_dir)
                config_manager = ConfigManager()
                
                expected_config_dir = Path(temp_dir) / '.voicerecorder'
                assert config_manager.config_dir == expected_config_dir
                assert config_manager.config_file == expected_config_dir / 'config.ini'
    
    def test_init_custom_config_dir(self):
        """Test initialization with custom config directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            assert config_manager.config_dir == Path(temp_dir)
            assert config_manager.config_file == Path(temp_dir) / 'config.ini'
    
    def test_ensure_config_dir(self):
        """Test config directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            config_manager._ensure_config_dir()
            
            assert Path(temp_dir).exists()
    
    def test_config_exists_true(self):
        """Test config_exists when file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            # Create a dummy config file
            config_file = Path(temp_dir) / 'config.ini'
            config_file.write_text('[test]\nkey=value')
            
            assert config_manager.config_exists()
    
    def test_config_exists_false(self):
        """Test config_exists when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            assert not config_manager.config_exists()
    
    def test_load_config_file_not_exists(self):
        """Test load_config when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            with pytest.raises(FileNotFoundError):
                config_manager.load_config()
    
    def test_load_config_file_exists(self):
        """Test load_config when file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            # Create a valid config file
            config_content = """
[audio]
sample_rate = 16000
channels = 1
format = wav
chunk_size = 1024

[transcription]
mode = openai_whisper
model_name = whisper-1

[hotkey]
key = shift
modifiers = 
description = Shift key for recording

[sound]
enabled = true
sound_type = tone
volume = 0.15
start_frequency = 800.0
end_frequency = 1200.0
duration = 0.3

[general]
auto_paste = true
temp_directory = /tmp
"""
            config_file = Path(temp_dir) / 'config.ini'
            config_file.write_text(config_content)
            
            config = config_manager.load_config()
            
            assert isinstance(config, ApplicationConfig)
            assert config.audio_config.sample_rate == 16000
            assert config.transcription_config.mode == TranscriptionMode.OPENAI_WHISPER
            assert config.hotkey_config.key == 'shift'
            assert config.sound_config.enabled is True
            assert config.auto_paste is True
    
    def test_save_config(self):
        """Test save_config method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            # Create a test config
            config = ApplicationConfig()
            
            config_manager.save_config(config)
            
            # Verify file was created
            assert config_manager.config_file.exists()
            
            # Verify content
            content = config_manager.config_file.read_text()
            assert '[audio]' in content
            assert '[transcription]' in content
            assert '[hotkey]' in content
            assert '[sound]' in content
            assert '[general]' in content
    
    def test_create_default_config(self):
        """Test create_default_config method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            config = config_manager.create_default_config()
            
            assert isinstance(config, ApplicationConfig)
            assert config_manager.config_file.exists()
    
    def test_get_config_path(self):
        """Test get_config_path method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            config_path = config_manager.get_config_path()
            
            assert config_path == str(Path(temp_dir) / 'config.ini')
    
    def test_get_temp_directory(self):
        """Test get_temp_directory method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            # Create a config with custom temp directory
            custom_temp_dir = Path(temp_dir) / 'custom_temp'
            config_content = f"""
[general]
temp_directory = {custom_temp_dir}
"""
            config_file = Path(temp_dir) / 'config.ini'
            config_file.write_text(config_content)
            
            temp_dir_path = config_manager.get_temp_directory()
            
            assert temp_dir_path == str(custom_temp_dir)
    
    def test_reset_to_defaults(self):
        """Test reset_to_defaults method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            # Create an existing config
            config_content = """
[audio]
sample_rate = 8000
"""
            config_file = Path(temp_dir) / 'config.ini'
            config_file.write_text(config_content)
            
            # Reset to defaults
            config = config_manager.reset_to_defaults()
            
            # Verify it was reset to default values
            assert config.audio_config.sample_rate == 16000  # Default value
    
    def test_update_config(self):
        """Test update_config method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            # Create initial config
            config = config_manager.create_default_config()
            
            # Update with new values
            updated_config = config_manager.update_config(
                transcription_config={
                    'mode': 'local_whisper',
                    'model_name': 'base'
                },
                audio_config={
                    'sample_rate': 22050
                }
            )
            
            # Verify updates
            assert updated_config.transcription_config.mode == TranscriptionMode.LOCAL_WHISPER
            assert updated_config.transcription_config.model_name == 'base'
            assert updated_config.audio_config.sample_rate == 22050 