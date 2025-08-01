"""
Welcome header widget for the main content area.
"""

import os

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)

from ..components.colors import FlowColors


class WelcomeHeader(QWidget):
    """Welcome header with user greeting and status"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = os.getenv("USER", "User")
        self.setup_ui()

    def setup_ui(self):
        """Setup the welcome header layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Welcome text
        self.welcome_label = QLabel(f"Welcome back, {self.current_user}")
        self.welcome_label.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_PRIMARY};
            font-size: 28px;
            font-weight: 600;
        """
        )

        layout.addWidget(self.welcome_label)
        layout.addStretch()

        # Status indicator
        self.status_label = QLabel("🔄 Initializing...")
        self.status_label.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_SECONDARY};
            font-size: 14px;
        """
        )

        layout.addWidget(self.status_label)

    def set_status(self, status_text: str):
        """Update the status text"""
        self.status_label.setText(status_text)

    def get_status_label(self):
        """Get the status label for external updates"""
        return self.status_label

    def hide_status(self):
        """Hide the status label completely"""
        self.status_label.hide()
