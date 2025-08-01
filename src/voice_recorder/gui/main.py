#!/usr/bin/env python3
"""
Voice Recorder - Refactored Main Window
Uses the new widget structure for a cleaner, more maintainable codebase.
"""

import sys
import os
from typing import Optional, List
import threading

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)

# Import our voice recorder components
from ..services.voice_recorder_service import VoiceRecorderService
from ..domain.models import (
    ApplicationConfig,
    RecordingSession,
    RecordingState,
)
from ..infrastructure.config_manager import ConfigManager
from ..infrastructure.audio_recorder import PyAudioRecorder
from ..infrastructure.transcription.factory import TranscriptionServiceFactory
from ..infrastructure.hotkey import PynputHotkeyListener
from ..infrastructure.text_paster import MacOSTextPaster
from ..infrastructure.session_manager import InMemorySessionManager
from ..infrastructure.audio_feedback import SystemAudioFeedback
from ..infrastructure.logging_adapter import LoggingAdapter

# Import GUI components
from .components import FlowColors, SystemTrayIcon, VoiceRecorderIcons
from .signals import RecordingStatusSignals, WindowControlSignals


class VoiceRecorderGUI(QMainWindow):
    """Refactored Voice Recorder with widget-based architecture"""

    def __init__(self):
        super().__init__()

        # Create signals for communication
        self.signals = RecordingStatusSignals()
        self.window_signals = WindowControlSignals()

        # Initialize voice recorder service
        self.voice_service: Optional[VoiceRecorderService] = None
        self.service_thread: Optional[threading.Thread] = None

        # System tray
        self.tray_icon: Optional[SystemTrayIcon] = None

        # Initialize components
        self.init_ui()
        self.init_system_tray()
        self.connect_signals()

        # Load session history for transcription display
        self.load_session_history()

        # Initialize configuration management only
        self.init_config_interface()

        # Skip animation (was causing visibility issues)
        # self.animate_window_entrance()

        # Force window to be visible with multiple methods
        self.show()
        self.showNormal()
        self.raise_()

        # Add entrance animation
        self.animate_dashboard_entrance()
        self.activateWindow()

        # Force to guaranteed visible position
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            safe_x = geometry.x() + 50
            safe_y = geometry.y() + 50
            self.move(safe_x, safe_y)

        # Additional visibility forcing
        QApplication.processEvents()
        self.setFocus()

        # TEMPORARY: Force window to stay on top until visible
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.show()  # Need to show again after changing flags

    def init_ui(self):
        """Initialize the main UI using widgets"""
        self.setWindowTitle("🎤 Voice Recorder")

        # Position window on primary screen center
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            # Center the window on the primary screen
            window_width, window_height = 1100, 750
            x = screen_geometry.x() + (screen_geometry.width() - window_width) // 2
            y = screen_geometry.y() + (screen_geometry.height() - window_height) // 2
            self.setGeometry(x, y, window_width, window_height)
        else:
            # Fallback if no screen info available
            self.setGeometry(100, 100, 1100, 750)

        self.setMinimumSize(900, 600)

        # Set application icon
        self.setWindowIcon(VoiceRecorderIcons.create_app_icon())

        # Main styling with modern gradient background
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
            }}
        """
        )

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - single screen without sidebar
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create stacked widget for main content and settings
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create main dashboard
        self.dashboard = self.create_dashboard()
        self.stacked_widget.addWidget(self.dashboard)

        # Create settings page
        self.settings_page = self.create_settings_page()
        self.stacked_widget.addWidget(self.settings_page)

        # Setup UI update timer
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(1000)  # Update every second

    def create_dashboard(self) -> QWidget:
        """Create the main dashboard widget"""
        dashboard = QWidget()
        dashboard.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95), stop:1 rgba(248, 250, 252, 0.95));
                border-radius: 24px;
                margin: 16px;
            }
        """
        )

        layout = QVBoxLayout(dashboard)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(28)

        # Header section with app name, icon and settings button
        header_section = QHBoxLayout()
        header_section.setContentsMargins(0, 0, 0, 16)

        # App icon and name
        app_info_layout = QHBoxLayout()
        app_info_layout.setSpacing(12)

        # App icon
        app_icon = QLabel("🎤")
        app_icon.setStyleSheet(
            f"""
            font-size: 28px;
            padding: 8px;
            background-color: {FlowColors.ACCENT_BLUE};
            border-radius: 12px;
            color: white;
            min-width: 40px;
            max-width: 40px;
            min-height: 40px;
            max-height: 40px;
        """
        )
        app_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_info_layout.addWidget(app_icon)

        # App name
        app_name = QLabel("Voice Recorder")
        app_name.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: 700;
            margin-left: 4px;
        """
        )
        app_info_layout.addWidget(app_name)

        header_section.addLayout(app_info_layout)
        header_section.addStretch()

        # Settings button in top-right corner
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setFixedSize(120, 40)
        self.settings_btn.setFont(QFont("Arial", 14, QFont.Weight.Medium))
        self.settings_btn.clicked.connect(self.show_settings)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 600;
                padding: 8px 16px;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a67d8, stop:1 #6b46c1);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}
        """
        )

        # Help button
        self.help_btn = QPushButton("❓ Help")
        self.help_btn.setFixedSize(80, 40)
        self.help_btn.setFont(QFont("Arial", 14, QFont.Weight.Medium))
        self.help_btn.clicked.connect(self.test_hotkey_detection)
        self.help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4ecdc4, stop:1 #44a08d);
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 600;
                padding: 8px 16px;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #26c6da, stop:1 #00acc1);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(78, 205, 196, 0.4);
            }}
        """
        )

        header_section.addWidget(self.help_btn)
        header_section.addWidget(self.settings_btn)

        layout.addLayout(header_section)

        # Statistics section
        stats_layout = QHBoxLayout()

        # Number of recordings card
        self.recordings_card = self.create_stat_card("🎤 Recordings", "0")
        stats_layout.addWidget(self.recordings_card)

        # Success rate card
        self.success_rate_card = self.create_stat_card("✅ Success Rate", "0%")
        stats_layout.addWidget(self.success_rate_card)

        # Words transcribed card (matching template's "success rate" label)
        self.words_card = self.create_stat_card("📝 Total Words", "0")
        stats_layout.addWidget(self.words_card)

        stats_layout.addStretch()

        layout.addLayout(stats_layout)

        # Conversation History section
        self.conversation_history = self.create_conversation_history_pane()
        layout.addWidget(self.conversation_history, 1)  # Give it more space

        return dashboard

    def create_stat_card(self, title: str, value: str) -> QWidget:
        """Create a modern statistics card widget with gradient and animations"""
        card = QWidget()
        card.setFixedSize(220, 140)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        # Determine gradient colors based on card type
        if "Recordings" in title:
            gradient_colors = "stop:0 #ff6b6b, stop:1 #ee5a52"
            hover_colors = "stop:0 #ff5252, stop:1 #e53935"
            icon = "🎤"
        elif "Success Rate" in title:
            gradient_colors = "stop:0 #4ecdc4, stop:1 #44a08d"
            hover_colors = "stop:0 #26c6da, stop:1 #00acc1"
            icon = "✅"
        else:  # Words
            gradient_colors = "stop:0 #45b7d1, stop:1 #96c93d"
            hover_colors = "stop:0 #29b6f6, stop:1 #66bb6a"
            icon = "📝"

        card.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    {gradient_colors});
                border: none;
                border-radius: 20px;
                color: white;
            }}
            QWidget:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    {hover_colors});
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Icon and title row
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            """
            font-size: 24px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 8px;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
        """
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            """
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
            font-weight: 600;
            background: none;
            border: none;
        """
        )
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        top_row.addWidget(icon_label)
        top_row.addStretch()
        top_row.addWidget(title_label)

        layout.addLayout(top_row)

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(
            """
            color: white;
            font-size: 32px;
            font-weight: 700;
            background: none;
            border: none;
        """
        )
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(value_label)
        layout.addStretch()

        # Store value label for updates
        if "Recordings" in title:
            self.recordings_value_label = value_label
        elif "Success Rate" in title:
            self.success_rate_value_label = value_label
        elif "Words" in title:
            self.words_value_label = value_label

        return card

    def create_conversation_history_pane(self) -> QWidget:
        """Create the modern conversation history pane showing last 5 conversations"""
        history_widget = QWidget()
        history_widget.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 2px solid #e2e8f0;
                border-radius: 24px;
                padding: 4px;
            }}
        """
        )

        layout = QVBoxLayout(history_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header with icon
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_icon = QLabel("💬")
        header_icon.setStyleSheet(
            """
            font-size: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #667eea, stop:1 #764ba2);
            border-radius: 10px;
            padding: 6px;
            color: white;
            min-width: 20px;
            max-width: 20px;
            min-height: 20px;
            max-height: 20px;
        """
        )
        header_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header = QLabel("Recent Conversations")
        header.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 700;
            margin-left: 12px;
            background: none;
            border: none;
        """
        )

        header_layout.addWidget(header_icon)
        header_layout.addWidget(header)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Scrollable area for conversations
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #f1f5f9, stop:1 #e2e8f0);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """
        )

        # Content widget for conversations
        self.conversations_content = QWidget()
        self.conversations_layout = QVBoxLayout(self.conversations_content)
        self.conversations_layout.setContentsMargins(0, 0, 0, 0)
        self.conversations_layout.setSpacing(12)

        # Initially show no conversations message
        no_conversations_label = QLabel(
            "No conversations yet.\nStart recording to see your transcriptions here."
        )
        no_conversations_label.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_SECONDARY};
            font-size: 14px;
            font-style: italic;
            text-align: center;
            padding: 20px;
        """
        )
        no_conversations_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.conversations_layout.addWidget(no_conversations_label)

        # Add stretch to push conversations to top
        self.conversations_layout.addStretch()

        scroll_area.setWidget(self.conversations_content)
        layout.addWidget(scroll_area)

        return history_widget

    def create_settings_page(self) -> QWidget:
        """Create the settings/preferences page"""
        settings = QWidget()
        layout = QVBoxLayout(settings)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header with back button
        header_layout = QHBoxLayout()

        back_btn = QPushButton("← Back to Dashboard")
        back_btn.clicked.connect(self.show_dashboard)
        back_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {FlowColors.TEXT_TERTIARY};
                color: {FlowColors.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {FlowColors.BORDER};
            }}
        """
        )
        header_layout.addWidget(back_btn)

        header_layout.addStretch()

        settings_title = QLabel("Settings & Preferences")
        settings_title.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: 600;
        """
        )
        header_layout.addWidget(settings_title)

        layout.addLayout(header_layout)

        # Settings form will be added here
        settings_form = QScrollArea()
        settings_form.setWidgetResizable(True)
        settings_form.setStyleSheet(
            f"""
            QScrollArea {{
                border: 1px solid {FlowColors.BORDER};
                border-radius: 8px;
                background-color: {FlowColors.CARD_BG};
            }}
        """
        )

        # Create settings form content
        form_widget = self.create_settings_form()
        settings_form.setWidget(form_widget)

        layout.addWidget(settings_form)

        return settings

    def create_settings_form(self) -> QWidget:
        """Create the settings form widget"""
        form_widget = QWidget()
        layout = QVBoxLayout(form_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Transcription Service Section
        transcription_group = QGroupBox("Transcription Service")
        transcription_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 16px;
                color: {FlowColors.TEXT_PRIMARY};
                border: 1px solid {FlowColors.BORDER};
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }}
        """
        )
        transcription_layout = QVBoxLayout(transcription_group)

        # Service type selection
        self.service_type_group = QButtonGroup()
        self.openai_radio = QRadioButton("OpenAI Whisper (Cloud)")
        self.local_radio = QRadioButton("Local Whisper (Offline)")
        self.mock_radio = QRadioButton("Mock Service (Testing)")

        self.service_type_group.addButton(self.openai_radio, 0)
        self.service_type_group.addButton(self.local_radio, 1)
        self.service_type_group.addButton(self.mock_radio, 2)

        transcription_layout.addWidget(self.openai_radio)
        transcription_layout.addWidget(self.local_radio)
        transcription_layout.addWidget(self.mock_radio)

        # OpenAI API Key field
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("OpenAI API Key:"))
        self.api_key_field = QLineEdit()
        self.api_key_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_field.setPlaceholderText("Enter your OpenAI API key")
        api_key_layout.addWidget(self.api_key_field)
        transcription_layout.addLayout(api_key_layout)

        # Model selection for local whisper
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Local Whisper Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        model_layout.addWidget(self.model_combo)
        transcription_layout.addLayout(model_layout)

        layout.addWidget(transcription_group)

        # Hotkey Configuration
        hotkey_group = QGroupBox("Hotkey Configuration")
        hotkey_group.setStyleSheet(transcription_group.styleSheet())
        hotkey_layout = QVBoxLayout(hotkey_group)

        hotkey_field_layout = QHBoxLayout()
        hotkey_field_layout.addWidget(QLabel("Recording Hotkey:"))
        self.hotkey_field = QLineEdit()
        self.hotkey_field.setPlaceholderText("e.g., shift_r, ctrl, alt")
        hotkey_field_layout.addWidget(self.hotkey_field)
        hotkey_layout.addLayout(hotkey_field_layout)

        layout.addWidget(hotkey_group)

        # Audio Configuration
        audio_group = QGroupBox("Audio Configuration")
        audio_group.setStyleSheet(transcription_group.styleSheet())
        audio_layout = QVBoxLayout(audio_group)

        # Auto-paste checkbox
        self.auto_paste_cb = QCheckBox("Auto-paste transcriptions")
        audio_layout.addWidget(self.auto_paste_cb)

        # Audio feedback checkbox
        self.audio_feedback_cb = QCheckBox("Enable audio feedback")
        audio_layout.addWidget(self.audio_feedback_cb)

        layout.addWidget(audio_group)

        # Save button
        save_btn = QPushButton("💾 Save Configuration")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_configuration)
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {FlowColors.ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #3367D6;
            }}
        """
        )
        layout.addWidget(save_btn)

        layout.addStretch()
        return form_widget

    def show_settings(self):
        """Show the settings page"""
        self.load_current_configuration()
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def show_dashboard(self):
        """Show the main dashboard"""
        self.stacked_widget.setCurrentWidget(self.dashboard)

    def load_current_configuration(self):
        """Load current configuration into the settings form"""
        try:
            config = self.config_manager.load_config()

            # Set transcription service type
            if config.transcription_config.mode.value == "openai_whisper":
                self.openai_radio.setChecked(True)
            elif config.transcription_config.mode.value == "local_whisper":
                self.local_radio.setChecked(True)
            else:
                self.mock_radio.setChecked(True)

            # Set API key
            if (
                hasattr(config.transcription_config, "api_key")
                and config.transcription_config.api_key
            ):
                self.api_key_field.setText(config.transcription_config.api_key)

            # Set model
            if hasattr(config.transcription_config, "model_name"):
                index = self.model_combo.findText(
                    config.transcription_config.model_name
                )
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)

            # Set hotkey
            self.hotkey_field.setText(config.hotkey_config.key)

            # Set checkboxes
            self.auto_paste_cb.setChecked(config.auto_paste)
            self.audio_feedback_cb.setChecked(config.sound_config.enabled)

        except Exception as e:
            QMessageBox.warning(
                self, "Configuration Error", f"Failed to load configuration: {str(e)}"
            )

    def save_configuration(self):
        """Save the configuration from the form"""
        try:
            # Get current config as base
            config = self.config_manager.load_config()

            # Update transcription service
            if self.openai_radio.isChecked():
                from ..domain.models import TranscriptionMode

                config.transcription_config.mode = TranscriptionMode.OPENAI_WHISPER
                config.transcription_config.api_key = self.api_key_field.text().strip()
            elif self.local_radio.isChecked():
                from ..domain.models import TranscriptionMode

                config.transcription_config.mode = TranscriptionMode.LOCAL_WHISPER
                config.transcription_config.model_name = self.model_combo.currentText()
            else:
                from ..domain.models import TranscriptionMode

                config.transcription_config.mode = TranscriptionMode.MOCK

            # Update hotkey
            config.hotkey_config.key = self.hotkey_field.text().strip()

            # Update other settings
            config.auto_paste = self.auto_paste_cb.isChecked()
            config.sound_config.enabled = self.audio_feedback_cb.isChecked()

            # Save configuration
            self.config_manager.save_config(config)

            QMessageBox.information(
                self,
                "Configuration Saved",
                "Configuration has been saved successfully!",
            )
            self.show_dashboard()

        except Exception as e:
            QMessageBox.critical(
                self, "Save Error", f"Failed to save configuration: {str(e)}"
            )

    def init_system_tray(self):
        """Initialize the system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                None, "System Tray", "System tray is not available on this system."
            )
            return

        self.tray_icon = SystemTrayIcon(self)

        # Connect tray signals to window signals
        self.tray_icon.show_window.connect(self.window_signals.show_window.emit)
        self.tray_icon.hide_window.connect(self.window_signals.hide_window.emit)
        self.tray_icon.quit_app.connect(self.window_signals.quit_application.emit)

    def connect_signals(self):
        """Connect all widget and component signals"""
        # Recording signals
        self.signals.recording_started.connect(self.on_recording_started)
        self.signals.recording_stopped.connect(self.on_recording_stopped)
        self.signals.transcription_completed.connect(self.on_transcription_completed)
        self.signals.recording_error.connect(self.on_recording_error)
        self.signals.session_updated.connect(self.on_session_updated)
        self.signals.processing_started.connect(self.on_processing_started)

        # Window control signals
        self.window_signals.show_window.connect(self.show_and_activate)
        self.window_signals.hide_window.connect(self.hide_to_tray)
        self.window_signals.quit_application.connect(self.quit_application)

    def init_config_interface(self):
        """Initialize configuration interface only - no recording services"""
        try:
            # Load configuration for display
            config_manager = ConfigManager()
            self.config = config_manager.load_config()
            self.config_manager = config_manager

            # Load and display statistics
            self.load_statistics()
            self.load_conversation_history()

        except Exception as e:
            print(f"Config error: {str(e)}")

    def load_statistics(self):
        """Load statistics from config file or initialize"""
        try:
            # Try to load statistics from config file
            import configparser
            import os

            config_dir = os.path.expanduser("~/.voicerecorder")
            stats_file = os.path.join(config_dir, "statistics.ini")

            if os.path.exists(stats_file):
                config = configparser.ConfigParser()
                config.read(stats_file)

                recordings = config.getint("Statistics", "total_recordings", fallback=0)
                successful = config.getint(
                    "Statistics", "successful_recordings", fallback=0
                )
                total_words = config.getint("Statistics", "total_words", fallback=0)
            else:
                recordings = 0
                successful = 0
                total_words = 0

            # Calculate success rate
            success_rate = (successful / recordings * 100) if recordings > 0 else 0

            # Update UI
            self.recordings_value_label.setText(str(recordings))
            self.success_rate_value_label.setText(f"{success_rate:.1f}%")
            self.words_value_label.setText(str(total_words))

        except Exception as e:
            print(f"Error loading statistics: {e}")
            self.recordings_value_label.setText("0")
            self.success_rate_value_label.setText("0%")
            self.words_value_label.setText("0")

    def load_conversation_history(self):
        """Load and display the last 5 conversations"""
        try:
            import configparser
            import os
            from datetime import datetime

            config_dir = os.path.expanduser("~/.voicerecorder")
            conversations_file = os.path.join(config_dir, "conversations.ini")

            # Clear existing conversations
            for i in reversed(range(self.conversations_layout.count())):
                child = self.conversations_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)

            conversations = []

            if os.path.exists(conversations_file):
                config = configparser.ConfigParser()
                config.read(conversations_file)

                # Get the last 5 conversations
                for i in range(1, 6):  # Last 5 conversations
                    section_name = f"Conversation_{i}"
                    if config.has_section(section_name):
                        text = config.get(section_name, "text", fallback="")
                        timestamp = config.get(section_name, "timestamp", fallback="")
                        if text:
                            conversations.append({"text": text, "timestamp": timestamp})

            if conversations:
                # Display conversations
                for i, conv in enumerate(conversations):
                    conv_widget = self.create_conversation_widget(
                        conv["text"], conv["timestamp"], i + 1
                    )
                    self.conversations_layout.addWidget(conv_widget)
            else:
                # Show no conversations message
                no_conversations_label = QLabel(
                    "No conversations yet.\nStart recording to see your transcriptions here."
                )
                no_conversations_label.setStyleSheet(
                    f"""
                    color: {FlowColors.TEXT_SECONDARY};
                    font-size: 14px;
                    font-style: italic;
                    text-align: center;
                    padding: 20px;
                """
                )
                no_conversations_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.conversations_layout.addWidget(no_conversations_label)

            # Add stretch to push conversations to top
            self.conversations_layout.addStretch()

        except Exception as e:
            print(f"Error loading conversation history: {e}")

    def create_conversation_widget(
        self, text: str, timestamp: str, number: int
    ) -> QWidget:
        """Create a modern widget for displaying a single conversation"""
        conv_widget = QWidget()
        conv_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        conv_widget.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin: 4px;
            }
            QWidget:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border: 2px solid #cbd5e1;
                transform: translateY(-2px);
            }
        """
        )

        layout = QVBoxLayout(conv_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header with number and timestamp
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Conversation number with modern badge
        number_label = QLabel(f"#{number}")
        number_label.setStyleSheet(
            """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #667eea, stop:1 #764ba2);
            color: white;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 10px;
            min-width: 16px;
            max-width: 40px;
        """
        )
        number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(number_label)

        header_layout.addStretch()

        # Timestamp with modern styling
        if timestamp:
            try:
                from datetime import datetime

                # Format timestamp nicely
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%m/%d %H:%M")
            except:
                formatted_time = timestamp[:16] if len(timestamp) > 16 else timestamp

            time_label = QLabel(formatted_time)
            time_label.setStyleSheet(
                """
                color: #64748b;
                font-size: 11px;
                font-weight: 500;
                background: #f1f5f9;
                padding: 4px 8px;
                border-radius: 8px;
            """
            )
            header_layout.addWidget(time_label)

        layout.addLayout(header_layout)

        # Conversation text with modern typography
        text_label = QLabel(text)
        text_label.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_PRIMARY};
            font-size: 14px;
            line-height: 1.6;
            font-weight: 400;
            background: none;
            border: none;
            padding: 4px 0px;
        """
        )
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(text_label)

        return conv_widget

    def update_statistics(self, new_transcript: str = None, success: bool = True):
        """Update statistics and save to config file"""
        try:
            import configparser
            import os

            config_dir = os.path.expanduser("~/.voicerecorder")
            os.makedirs(config_dir, exist_ok=True)
            stats_file = os.path.join(config_dir, "statistics.ini")

            # Load existing stats
            config = configparser.ConfigParser()
            if os.path.exists(stats_file):
                config.read(stats_file)

            if not config.has_section("Statistics"):
                config.add_section("Statistics")

            # Get current values
            recordings = config.getint("Statistics", "total_recordings", fallback=0)
            successful = config.getint(
                "Statistics", "successful_recordings", fallback=0
            )
            total_words = config.getint("Statistics", "total_words", fallback=0)

            # Update values
            recordings += 1
            if success:
                successful += 1
                if new_transcript:
                    word_count = len(new_transcript.split())
                    total_words += word_count

            # Save updated stats
            config.set("Statistics", "total_recordings", str(recordings))
            config.set("Statistics", "successful_recordings", str(successful))
            config.set("Statistics", "total_words", str(total_words))

            with open(stats_file, "w") as f:
                config.write(f)

            # Update display
            self.load_statistics()

            # Update conversation history if we have a new transcript
            if new_transcript and success:
                self.add_conversation(new_transcript)

        except Exception as e:
            print(f"Error updating statistics: {e}")

    def add_conversation(self, transcript: str):
        """Add a new conversation to the history"""
        try:
            import configparser
            import os
            from datetime import datetime

            config_dir = os.path.expanduser("~/.voicerecorder")
            os.makedirs(config_dir, exist_ok=True)
            conversations_file = os.path.join(config_dir, "conversations.ini")

            config = configparser.ConfigParser()
            if os.path.exists(conversations_file):
                config.read(conversations_file)

            # Shift existing conversations down (5 -> 4, 4 -> 3, etc.)
            for i in range(4, 0, -1):  # 4, 3, 2, 1
                old_section = f"Conversation_{i}"
                new_section = f"Conversation_{i+1}"

                if config.has_section(old_section):
                    # Copy section to new position
                    if not config.has_section(new_section):
                        config.add_section(new_section)
                    for option in config.options(old_section):
                        value = config.get(old_section, option)
                        config.set(new_section, option, value)

            # Add new conversation as #1
            section_name = "Conversation_1"
            if not config.has_section(section_name):
                config.add_section(section_name)

            config.set(section_name, "text", transcript)
            config.set(section_name, "timestamp", datetime.now().isoformat())

            with open(conversations_file, "w") as f:
                config.write(f)

            # Update display
            self.load_conversation_history()

        except Exception as e:
            print(f"Error adding conversation: {e}")

    def init_voice_service(self):
        """Initialize the voice recorder service"""
        try:
            # Initialize console interface
            console = LoggingAdapter()

            # Initialize components and load configuration
            config_manager = ConfigManager()
            config = config_manager.load_config()
            audio_recorder = PyAudioRecorder(console=console)
            transcription_factory = TranscriptionServiceFactory()
            transcription_service = transcription_factory.create_service(
                config.transcription_config
            )
            hotkey_listener = PynputHotkeyListener(console=console)
            text_paster = MacOSTextPaster(console=console)
            session_manager = InMemorySessionManager()
            audio_feedback = SystemAudioFeedback(console=console)

            # Create voice recorder service
            self.voice_service = VoiceRecorderService(
                audio_recorder=audio_recorder,
                transcription_service=transcription_service,
                hotkey_listener=hotkey_listener,
                text_paster=text_paster,
                session_manager=session_manager,
                audio_feedback=audio_feedback,
                config=config,
                console=console,
            )

            # Override service callbacks to emit our signals
            self.setup_service_callbacks()

            # Start the service in a separate thread
            self.service_thread = threading.Thread(
                target=self.voice_service.start, daemon=True
            )
            self.service_thread.start()

            # Service started successfully - just set tray icon
            if self.tray_icon:
                self.tray_icon.set_ready_state()

        except Exception as e:
            error_msg = f"❌ Service error: {str(e)}"
            print(error_msg)  # Log to console instead
            if self.tray_icon:
                self.tray_icon.set_error_state()
            QMessageBox.critical(
                self,
                "Service Error",
                f"Failed to initialize voice recorder service:\n{str(e)}",
            )

    def setup_service_callbacks(self):
        """Setup voice service callbacks to emit GUI signals"""
        original_start = self.voice_service._start_recording
        original_stop = self.voice_service._stop_recording_and_process

        def start_with_signal():
            original_start()
            self.signals.recording_started.emit()

        def stop_with_signal():
            try:
                self.signals.processing_started.emit()
                original_stop()
                if self.voice_service.current_session:
                    self.signals.session_updated.emit(
                        self.voice_service.current_session
                    )
                    if self.voice_service.current_session.transcript:
                        self.signals.transcription_completed.emit(
                            self.voice_service.current_session.transcript
                        )
                self.signals.recording_stopped.emit()
            except Exception as e:
                self.signals.recording_error.emit(str(e))

        self.voice_service._start_recording = start_with_signal
        self.voice_service._stop_recording_and_process = stop_with_signal

    def animate_window_entrance(self):
        """Animate window entrance"""
        self.setWindowOpacity(0.0)

        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(600)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)

        QTimer.singleShot(200, animation.start)

    def animate_dashboard_entrance(self):
        """Animate the dashboard entrance with fade and slide effects"""
        if hasattr(self, "dashboard"):
            # Start with dashboard hidden
            self.dashboard.setStyleSheet(
                """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(255, 255, 255, 0.95), stop:1 rgba(248, 250, 252, 0.95));
                    border-radius: 24px;
                    margin: 16px;
                }
            """
            )

            # Create opacity animation
            self.opacity_effect = QGraphicsOpacityEffect()
            self.dashboard.setGraphicsEffect(self.opacity_effect)

            self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.opacity_animation.setDuration(800)
            self.opacity_animation.setStartValue(0.0)
            self.opacity_animation.setEndValue(1.0)
            self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            # Start animation after a short delay
            QTimer.singleShot(100, self.opacity_animation.start)

    # Window management
    def show_and_activate(self):
        """Show and activate the main window"""
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        if self.tray_icon:
            self.tray_icon.show_notification(
                "Voice Recorder", "Application minimized to tray", 2000
            )

    def quit_application(self):
        """Quit the entire application"""
        self.close()

    def closeEvent(self, event):
        """Handle close event - minimize to tray instead of closing"""
        if self.tray_icon and self.tray_icon.isVisible():
            # If system tray is available, minimize to tray
            event.ignore()
            self.hide_to_tray()
        else:
            # If no system tray, actually quit
            self.cleanup_and_quit()
            event.accept()

    def cleanup_and_quit(self):
        """Clean up resources and quit"""
        if self.voice_service:
            try:
                self.voice_service.stop()
            except Exception as e:
                print(f"Error stopping voice service: {e}")

        if self.tray_icon:
            self.tray_icon.hide()

        QApplication.quit()

    # UI update methods
    def update_ui(self):
        """Update UI elements periodically"""
        # UI updates are now handled through statistics and transcript updates
        pass

    def load_session_history(self):
        """Load and display session history"""
        # Session history is now loaded from persistent files
        self.load_statistics()
        self.load_conversation_history()

    # Signal handlers
    def on_recording_started(self):
        """Handle recording started"""
        if self.tray_icon:
            self.tray_icon.set_recording_state()

    def on_processing_started(self):
        """Handle transcription processing started"""
        if self.tray_icon:
            self.tray_icon.set_processing_state()

    def on_recording_stopped(self):
        """Handle recording stopped"""
        if self.tray_icon:
            self.tray_icon.set_ready_state()

    def on_transcription_completed(self, text: str):
        """Handle transcription completed"""
        # Update statistics with the new transcript
        self.update_statistics(text, success=True)

        if self.tray_icon:
            self.tray_icon.show_notification(
                "Transcription Complete", f"Transcribed: {text[:50]}..."
            )

    def on_recording_error(self, error_message: str):
        """Handle recording error"""
        # Update statistics for failed recording
        self.update_statistics(success=False)

        QMessageBox.warning(
            self, "Recording Error", f"An error occurred:\n{error_message}"
        )

        if self.tray_icon:
            self.tray_icon.set_error_state()

    def on_session_updated(self, session: RecordingSession):
        """Handle session update"""
        # Statistics are updated in transcription_completed handler
        pass

    # Action handlers (most removed since GUI is config-only now)

    def test_hotkey_detection(self):
        """Test hotkey detection and provide feedback."""
        if not self.voice_service:
            QMessageBox.warning(
                self, "Service Not Ready", "Voice recorder service is not initialized."
            )
            return

        # Get the configured hotkey
        hotkey = self.voice_service.config.hotkey_config.key
        description = self.voice_service.config.hotkey_config.description

        # Show a test dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Hotkey Test")
        msg.setText(f"Hotkey Detection Test")
        msg.setInformativeText(
            f"Configured hotkey: {hotkey} ({description})\n\n"
            "Press the hotkey now to test if it's being detected.\n"
            "If you see debug messages in the console, the hotkey is working.\n\n"
            "If hotkeys don't work, you can use the manual recording button instead."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        # Update status label with hotkey info
        self.recording_status_label.setText(
            f"Hotkey: {description} (or click to record)"
        )

    def show_help(self):
        """Show help dialog"""
        QMessageBox.information(
            self,
            "Help",
            "Voice Recorder Configuration Interface\n\n"
            "This GUI provides configuration and monitoring capabilities:\n\n"
            "Configuration:\n"
            "• Access settings via the sidebar\n"
            "• Configure transcription services (OpenAI/Local Whisper)\n"
            "• Set up API keys and preferences\n"
            "• Adjust hotkeys and audio feedback\n\n"
            "Monitoring:\n"
            "• View transcription history\n"
            "• Monitor recording statistics\n"
            "• Export session data\n\n"
            "To Record:\n"
            "Run 'voice-recorder' in terminal and use your configured hotkey.\n"
            "Recording functionality is handled by the CLI background service.",
        )


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Voice Recorder")
    app.setOrganizationName("Voice Recorder Team")
    app.setApplicationVersion("1.0")

    # macOS optimizations
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, True)

    # Don't quit when last window is closed (for tray functionality)
    app.setQuitOnLastWindowClosed(False)

    # Create and show main window
    window = VoiceRecorderGUI()
    window.show()

    # Ensure window visibility on macOS
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
