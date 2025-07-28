"""
Unit tests for text paster components.
"""

import tempfile
from unittest.mock import Mock, patch

import pytest

from src.voice_recorder.infrastructure.text_paster import MacOSTextPaster


class TestMacOSTextPaster:
    """Test cases for MacOSTextPaster."""

    def test_init(self):
        """Test MacOSTextPaster initialization."""
        paster = MacOSTextPaster()
        assert paster is not None

    @patch('subprocess.run')
    @patch('subprocess.Popen')
    def test_paste_text(self, mock_popen, mock_run):
        """Test paste_text method."""
        paster = MacOSTextPaster()
        test_text = "Hello, world!"
        
        # Mock Popen for clipboard copy
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        # Mock run for AppleScript
        mock_run.return_value = Mock()
        
        result = paster.paste_text(test_text)
        
        # Should call Popen for pbcopy
        mock_popen.assert_called_once()
        # Should call run for AppleScript
        mock_run.assert_called_once()
        assert result is True

    @patch('subprocess.run')
    def test_paste_at_mouse_position(self, mock_run):
        """Test _paste_at_mouse_position method."""
        paster = MacOSTextPaster()
        
        # Mock run for AppleScript
        mock_run.return_value = Mock()
        
        result = paster._paste_at_mouse_position()
        
        # Should call run for AppleScript
        mock_run.assert_called_once()
        assert result is True

    @patch('subprocess.run')
    @patch('subprocess.Popen')
    def test_paste_text_with_mouse_position(self, mock_popen, mock_run):
        """Test paste_text with mouse position."""
        paster = MacOSTextPaster()
        test_text = "Hello, world!"
        
        # Mock Popen for clipboard copy
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        # Mock run for AppleScript
        mock_run.return_value = Mock()
        
        result = paster.paste_text(test_text, position="mouse")
        
        # Should call Popen for pbcopy and run for AppleScript
        mock_popen.assert_called_once()
        mock_run.assert_called_once()
        assert result is True

    @patch('subprocess.run', side_effect=Exception("Command failed"))
    def test_paste_text_error(self, mock_run):
        """Test paste_text with subprocess error."""
        paster = MacOSTextPaster()
        test_text = "Hello, world!"
        
        # Should not raise exception, just print error
        paster.paste_text(test_text)
        
        mock_run.assert_called_once() 