"""
Statistics section widget showing recording metrics.
"""

from typing import List

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)

from ..components import FlowColors, FlowStatCard
from ...domain.models import RecordingSession, RecordingState


class StatisticsSection(QWidget):
    """Statistics cards section with live data"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_recordings = 0
        self.total_words = 0
        self.setup_ui()

    def setup_ui(self):
        """Setup the statistics section layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Recording count card
        self.recordings_card = FlowStatCard(
            "🎤", "0", "recordings", FlowColors.ACCENT_BLUE
        )
        layout.addWidget(self.recordings_card)

        # Words transcribed card
        self.words_card = FlowStatCard(
            "✏️", "0 words", "transcribed", FlowColors.ACCENT_GREEN
        )
        layout.addWidget(self.words_card)

        # Success rate card
        self.success_card = FlowStatCard(
            "✅", "0%", "success rate", FlowColors.ACCENT_ORANGE
        )
        layout.addWidget(self.success_card)

        layout.addStretch()

    def update_statistics(self, sessions: List[RecordingSession]):
        """Update statistics cards with session data"""
        completed_sessions = [
            s for s in sessions if s.state == RecordingState.COMPLETED
        ]

        # Update recordings count
        self.total_recordings = len(completed_sessions)
        self.recordings_card.update_value(str(self.total_recordings))

        # Update words count
        total_words = 0
        for session in completed_sessions:
            if session.transcript:
                total_words += len(session.transcript.split())

        self.total_words = total_words
        self.words_card.update_value(f"{total_words} words")

        # Update success rate
        total_sessions = len(sessions)
        if total_sessions > 0:
            success_rate = int((len(completed_sessions) / total_sessions) * 100)
            self.success_card.update_value(f"{success_rate}%")
        else:
            self.success_card.update_value("0%")
