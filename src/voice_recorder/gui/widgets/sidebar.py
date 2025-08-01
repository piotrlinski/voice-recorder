"""
Sidebar widget for navigation.
"""

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)

from ..components import FlowColors, FlowSidebarItem


class Sidebar(QWidget):
    """Flow-style sidebar navigation"""

    # Signals
    page_changed = pyqtSignal(str)  # page name
    help_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_items = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the sidebar layout"""
        self.setFixedWidth(220)
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {FlowColors.SIDEBAR_BG};
                border-right: 1px solid {FlowColors.BORDER};
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)

        # App header
        self.create_app_header(layout)
        layout.addSpacing(16)

        # Navigation items
        self.create_navigation_items(layout)

        layout.addStretch()

        # Settings section
        self.create_settings_section(layout)

    def create_app_header(self, layout):
        """Create the app header with logo and title"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # App icon/logo
        logo_label = QLabel("🎤")
        logo_label.setFixedSize(24, 24)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 18px;")

        # App name
        app_name = QLabel("Voice Recorder")
        app_name.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
        """
        )

        # Pro badge
        pro_badge = QLabel("Desktop")
        pro_badge.setFixedHeight(20)
        pro_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pro_badge.setStyleSheet(
            f"""
            background-color: {FlowColors.ACCENT_PURPLE};
            color: white;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 500;
            padding: 0 8px;
        """
        )

        header_layout.addWidget(logo_label)
        header_layout.addWidget(app_name)
        header_layout.addStretch()
        header_layout.addWidget(pro_badge)

        layout.addLayout(header_layout)

    def create_navigation_items(self, layout):
        """Create the main navigation items"""
        self.home_item = FlowSidebarItem("🏠", "Home")
        self.home_item.set_selected(True)
        self.home_item.clicked.connect(lambda: self.set_active_page("home"))
        self.nav_items.append(self.home_item)
        layout.addWidget(self.home_item)

        self.recordings_item = FlowSidebarItem("🎵", "Recordings")
        self.recordings_item.clicked.connect(lambda: self.set_active_page("recordings"))
        self.nav_items.append(self.recordings_item)
        layout.addWidget(self.recordings_item)

        self.transcripts_item = FlowSidebarItem("📝", "Transcripts")
        self.transcripts_item.clicked.connect(
            lambda: self.set_active_page("transcripts")
        )
        self.nav_items.append(self.transcripts_item)
        layout.addWidget(self.transcripts_item)

    def create_settings_section(self, layout):
        """Create the settings section"""
        # Settings section
        settings_title = QLabel("SETTINGS")
        settings_title.setFont(QFont("SF Pro Text", 11, QFont.Weight.DemiBold))
        settings_title.setStyleSheet(
            f"color: {FlowColors.TEXT_SECONDARY}; margin-bottom: 8px;"
        )
        layout.addWidget(settings_title)

        self.preferences_item = FlowSidebarItem("⚙️", "Preferences")
        self.preferences_item.clicked.connect(
            lambda: self.set_active_page("preferences")
        )
        self.nav_items.append(self.preferences_item)
        layout.addWidget(self.preferences_item)

        # Help section
        help_item = FlowSidebarItem("❓", "Help")
        help_item.clicked.connect(self.help_requested.emit)
        layout.addWidget(help_item)

    def set_active_page(self, page_name: str):
        """Set active navigation page"""
        # Reset all items
        for item in self.nav_items:
            item.set_selected(False)

        # Set active item
        if page_name == "home":
            self.home_item.set_selected(True)
        elif page_name == "recordings":
            self.recordings_item.set_selected(True)
        elif page_name == "transcripts":
            self.transcripts_item.set_selected(True)
        elif page_name == "preferences":
            self.preferences_item.set_selected(True)

        # Emit signal
        self.page_changed.emit(page_name)
