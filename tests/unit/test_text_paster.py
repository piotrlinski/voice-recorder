"""
Unit tests for text paster functionality.
"""

import os
import subprocess
from unittest.mock import Mock, patch

import pytest

from src.voice_recorder.infrastructure.text_paster import MacOSTextPaster


class TestMacOSTextPaster:
    """Test cases for MacOSTextPaster."""

    def test_init(self, mock_console):
        """Test MacOSTextPaster initialization."""
        paster = MacOSTextPaster(console=mock_console)
        assert paster.console == mock_console

    @patch('subprocess.run')
    def test_paste_text(self, mock_run, mock_console):
        """Test paste_text method."""
        mock_run.return_value = Mock(returncode=0)
        
        paster = MacOSTextPaster(console=mock_console)
        paster.paste_text("Hello, world!")
        
        mock_run.assert_called_once()
        mock_console.print_success.assert_called_once_with("📋 Text pasted successfully")

    @patch('subprocess.run')
    def test_paste_at_mouse_position(self, mock_run, mock_console):
        """Test paste_at_mouse_position method."""
        mock_run.return_value = Mock(returncode=0)
        
        paster = MacOSTextPaster(console=mock_console)
        paster.paste_at_mouse_position("Hello, world!")
        
        # Should be called once for the osascript command
        assert mock_run.call_count == 1
        mock_console.print_success.assert_called_once_with("📋 Text pasted at mouse position")

    @patch('subprocess.run')
    def test_paste_text_with_mouse_position(self, mock_run, mock_console):
        """Test paste_text_with_mouse_position method."""
        mock_run.return_value = Mock(returncode=0, stdout=b"100 200")
        
        paster = MacOSTextPaster(console=mock_console)
        paster.paste_text_with_mouse_position("Hello, world!")
        
        # Should be called twice: once for getting mouse position, once for pasting
        assert mock_run.call_count == 2
        mock_console.print_success.assert_called_once_with("📋 Text pasted at mouse position")

    @patch('subprocess.run')
    def test_paste_text_error(self, mock_run, mock_console):
        """Test paste_text method with error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "osascript")
        
        paster = MacOSTextPaster(console=mock_console)
        paster.paste_text("Hello, world!")
        
        mock_console.print_error.assert_called_once_with("Text pasting failed: Command 'osascript' returned non-zero exit status 1.")

    @patch('subprocess.run')
    def test_paste_text_clipboard_failure(self, mock_run, mock_console):
        """Test paste_text method with clipboard failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "pbcopy")
        
        paster = MacOSTextPaster(console=mock_console)
        paster.paste_text("Hello, world!")
        
        mock_console.print_error.assert_called_once_with("Text pasting failed: Command 'pbcopy' returned non-zero exit status 1.")

    @patch('subprocess.run')
    def test_paste_text_with_position_mouse(self, mock_run, mock_console):
        """Test paste_text_with_position method with mouse position."""
        mock_run.return_value = Mock(returncode=0, stdout=b"100 200")
        
        paster = MacOSTextPaster(console=mock_console)
        paster.paste_text_with_position("Hello, world!", position="mouse")
        
        # Should be called once for the osascript command
        assert mock_run.call_count == 1
        mock_console.print_success.assert_called_once_with("📋 Text pasted at mouse position")

    @patch('subprocess.run')
    def test_paste_text_with_position_default(self, mock_run, mock_console):
        """Test paste_text_with_position method with default position."""
        mock_run.return_value = Mock(returncode=0)
        
        paster = MacOSTextPaster(console=mock_console)
        paster.paste_text_with_position("Hello, world!", position="default")
        
        # Should be called once for pasting
        assert mock_run.call_count == 1
        mock_console.print_success.assert_called_once_with("📋 Text pasted successfully") 