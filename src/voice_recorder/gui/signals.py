"""
Signal handlers and communication classes for the GUI.
"""

try:
    from PyQt6.QtCore import QObject, pyqtSignal
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)


class RecordingStatusSignals(QObject):
    """Signals for recording status updates"""

    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    transcription_completed = pyqtSignal(str)  # transcribed text
    recording_error = pyqtSignal(str)  # error message
    session_updated = pyqtSignal(object)  # RecordingSession object
    processing_started = pyqtSignal()  # transcription processing started


class WindowControlSignals(QObject):
    """Signals for window control from system tray"""

    show_window = pyqtSignal()
    hide_window = pyqtSignal()
    quit_application = pyqtSignal()
    toggle_recording = pyqtSignal()  # Toggle recording from tray
