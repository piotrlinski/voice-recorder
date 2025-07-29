"""
Unit tests for hotkey components.
"""

from unittest.mock import Mock, patch

import pytest

from src.voice_recorder.infrastructure.hotkey import PynputHotkeyListener


class TestPynputHotkeyListener:
    """Test cases for PynputHotkeyListener."""

    def test_init_without_pynput(self):
        """Test initialization when pynput is not available."""
        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(RuntimeError, match="Pynput library not available"):
                PynputHotkeyListener()

    def test_init_with_pynput(self):
        """Test initialization when pynput is available."""
        mock_keyboard = Mock()
        with patch('builtins.__import__', return_value=mock_keyboard):
            listener = PynputHotkeyListener()
            assert listener.keyboard is not None

    def test_start_listening(self):
        """Test start_listening method."""
        mock_keyboard = Mock()
        mock_listener = Mock()
        mock_keyboard.Listener.return_value = mock_listener
        
        with patch('builtins.__import__', return_value=mock_keyboard):
            listener = PynputHotkeyListener()
            
            def on_press(key):
                pass
            
            def on_release(key):
                pass
            
            # Set callbacks first
            listener.set_callbacks(on_press, on_release)
            listener.start_listening()
            
            assert listener.on_press_callback == on_press
            assert listener.on_release_callback == on_release
            # The Listener is created and started
            assert listener.listener is not None

    def test_stop_listening(self):
        """Test stop_listening method."""
        mock_keyboard = Mock()
        mock_listener = Mock()
        mock_keyboard.Listener.return_value = mock_listener
        
        with patch('builtins.__import__', return_value=mock_keyboard):
            listener = PynputHotkeyListener()
            listener.listener = mock_listener
            
            listener.stop_listening()
            
            mock_listener.stop.assert_called_once()
            assert listener.listener is None

    def test_on_press_handler(self):
        """Test _on_press handler."""
        mock_keyboard = Mock()
        with patch('builtins.__import__', return_value=mock_keyboard):
            listener = PynputHotkeyListener()
            
            mock_callback = Mock()
            listener.on_press_callback = mock_callback
            
            test_key = Mock()
            listener._on_press(test_key)
            
            mock_callback.assert_called_once_with(test_key)

    def test_on_release_handler(self):
        """Test _on_release handler."""
        mock_keyboard = Mock()
        with patch('builtins.__import__', return_value=mock_keyboard):
            listener = PynputHotkeyListener()
            
            mock_callback = Mock()
            listener.on_release_callback = mock_callback
            
            test_key = Mock()
            listener._on_release(test_key)
            
            mock_callback.assert_called_once_with(test_key)


class MockHotkeyListener:
    """Mock hotkey listener for testing."""

    def __init__(self):
        self.is_listening = False
        self.on_press_callback = None
        self.on_release_callback = None

    def start_listening(self, on_press, on_release):
        """Start listening for hotkey events."""
        self.is_listening = True
        self.on_press_callback = on_press
        self.on_release_callback = on_release

    def stop_listening(self):
        """Stop listening for hotkey events."""
        self.is_listening = False

    def simulate_key_press(self, key):
        """Simulate a key press event."""
        if self.on_press_callback:
            self.on_press_callback(key)

    def simulate_key_release(self, key):
        """Simulate a key release event."""
        if self.on_release_callback:
            self.on_release_callback(key)


class TestMockHotkeyListener:
    """Test cases for MockHotkeyListener."""

    def test_init(self):
        """Test MockHotkeyListener initialization."""
        listener = MockHotkeyListener()
        assert listener.is_listening is False
        assert listener.on_press_callback is None
        assert listener.on_release_callback is None

    def test_start_listening(self):
        """Test start_listening method."""
        listener = MockHotkeyListener()
        
        def on_press(key):
            pass
        
        def on_release(key):
            pass
        
        listener.start_listening(on_press, on_release)
        
        assert listener.is_listening is True
        assert listener.on_press_callback == on_press
        assert listener.on_release_callback == on_release

    def test_stop_listening(self):
        """Test stop_listening method."""
        listener = MockHotkeyListener()
        listener.is_listening = True
        
        listener.stop_listening()
        
        assert listener.is_listening is False

    def test_simulate_key_press(self):
        """Test simulate_key_press method."""
        listener = MockHotkeyListener()
        mock_callback = Mock()
        listener.on_press_callback = mock_callback
        listener.is_listening = True
        
        test_key = Mock()
        listener.simulate_key_press(test_key)
        
        mock_callback.assert_called_once_with(test_key)

    def test_simulate_key_release(self):
        """Test simulate_key_release method."""
        listener = MockHotkeyListener()
        mock_callback = Mock()
        listener.on_release_callback = mock_callback
        listener.is_listening = True
        
        test_key = Mock()
        listener.simulate_key_release(test_key)
        
        mock_callback.assert_called_once_with(test_key) 