"""
Main content area widget that combines all content sections.
"""

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)

from .welcome_header import WelcomeHeader
from .statistics_section import StatisticsSection
from .recording_controls import RecordingControls
from .transcriptions_section import TranscriptionsSection


class ContentArea(QWidget):
    """Main content area combining all sections"""

    # Forward signals from child widgets
    manual_recording_toggled = pyqtSignal()
    transcription_copied = pyqtSignal(str)
    transcriptions_cleared = pyqtSignal()
    transcriptions_exported = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the main content area layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Welcome header
        self.welcome_header = WelcomeHeader()
        layout.addWidget(self.welcome_header)

        # Statistics cards
        self.statistics_section = StatisticsSection()
        layout.addWidget(self.statistics_section)

        # Recording controls
        self.recording_controls = RecordingControls()
        layout.addWidget(self.recording_controls)

        # Recent transcriptions
        self.transcriptions_section = TranscriptionsSection()
        layout.addWidget(self.transcriptions_section, 1)

    def connect_signals(self):
        """Connect child widget signals to forward them"""
        self.recording_controls.manual_recording_toggled.connect(
            self.manual_recording_toggled.emit
        )
        self.transcriptions_section.transcription_copied.connect(
            self.transcription_copied.emit
        )
        self.transcriptions_section.transcriptions_cleared.connect(
            self.transcriptions_cleared.emit
        )
        self.transcriptions_section.transcriptions_exported.connect(
            self.transcriptions_exported.emit
        )

    # Convenience methods to access child widgets
    def get_welcome_header(self) -> WelcomeHeader:
        """Get the welcome header widget"""
        return self.welcome_header

    def get_statistics_section(self) -> StatisticsSection:
        """Get the statistics section widget"""
        return self.statistics_section

    def get_recording_controls(self) -> RecordingControls:
        """Get the recording controls widget"""
        return self.recording_controls

    def get_transcriptions_section(self) -> TranscriptionsSection:
        """Get the transcriptions section widget"""
        return self.transcriptions_section
