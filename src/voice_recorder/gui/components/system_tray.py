"""
System tray icon with recording status indication.
"""

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)

from .icons import VoiceRecorderIcons


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon that changes color based on recording status"""

    # Signals
    show_window = pyqtSignal()
    hide_window = pyqtSignal()
    quit_app = pyqtSignal()
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize with green (ready) icon
        self.set_ready_state()

        # Create context menu
        self.create_context_menu()

        # Connect activation signal
        self.activated.connect(self.on_tray_activated)

        # Show the tray icon
        self.show()

    def create_context_menu(self):
        """Create the system tray context menu"""
        menu = QMenu()

        # Only quit action
        quit_action = QAction("Quit Application", self)
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - could show a quick status tooltip
            pass

    def set_ready_state(self):
        """Set tray icon to green (ready to record)"""
        icon = VoiceRecorderIcons.create_ready_icon()
        self.setIcon(icon)
        self.setToolTip("Voice Recorder - Ready")

    def set_recording_state(self):
        """Set tray icon to red (recording active)"""
        icon = VoiceRecorderIcons.create_recording_icon()
        self.setIcon(icon)
        self.setToolTip("Voice Recorder - Recording...")

    def set_processing_state(self):
        """Set tray icon to orange (processing transcription)"""
        icon = VoiceRecorderIcons.create_processing_icon()
        self.setIcon(icon)
        self.setToolTip("Voice Recorder - Processing...")

    def set_error_state(self):
        """Set tray icon to gray (error state)"""
        icon = VoiceRecorderIcons.create_error_icon()
        self.setIcon(icon)
        self.setToolTip("Voice Recorder - Error")

    def show_notification(self, title: str, message: str, duration: int = 3000):
        """Show a system notification"""
        if self.supportsMessages():
            self.showMessage(
                title, message, QSystemTrayIcon.MessageIcon.Information, duration
            )
