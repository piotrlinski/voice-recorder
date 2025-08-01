"""
UI Widgets package for Voice Recorder GUI.
"""

from .content_area import ContentArea
from .sidebar import Sidebar
from .welcome_header import WelcomeHeader
from .statistics_section import StatisticsSection
from .recording_controls import RecordingControls
from .transcriptions_section import TranscriptionsSection

__all__ = [
    "ContentArea",
    "Sidebar",
    "WelcomeHeader",
    "StatisticsSection",
    "RecordingControls",
    "TranscriptionsSection",
]
