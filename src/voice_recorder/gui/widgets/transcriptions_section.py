"""
Transcriptions section widget for displaying and managing transcripts.
"""

import json
import os
from datetime import datetime
from typing import List

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)

from ..components.colors import FlowColors
from ...domain.models import RecordingSession, RecordingState


class TranscriptionsSection(QGroupBox):
    """Recent transcriptions section with management controls"""

    # Signals
    transcription_copied = pyqtSignal(str)  # message
    transcriptions_cleared = pyqtSignal()
    transcriptions_exported = pyqtSignal(str)  # filename

    def __init__(self, parent=None):
        super().__init__("Recent Transcriptions", parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the transcriptions section layout"""
        self.setStyleSheet(
            f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 16px;
                color: {FlowColors.TEXT_PRIMARY};
                border: 1px solid {FlowColors.BORDER};
                border-radius: 12px;
                margin-top: 8px;
                background-color: {FlowColors.CARD_BG};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: {FlowColors.CARD_BG};
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Transcriptions list
        self.transcriptions_list = QListWidget()
        self.transcriptions_list.setStyleSheet(
            f"""
            QListWidget {{
                border: none;
                background-color: transparent;
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 12px;
                margin: 4px 0;
                border-radius: 8px;
                background-color: {FlowColors.SIDEBAR_BG};
                border: 1px solid {FlowColors.BORDER};
            }}
            QListWidget::item:hover {{
                background-color: {FlowColors.SIDEBAR_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {FlowColors.SIDEBAR_SELECTED};
                color: {FlowColors.ACCENT_BLUE};
            }}
        """
        )

        # Action buttons
        button_layout = QHBoxLayout()

        copy_btn = QPushButton("Copy Selected")
        copy_btn.clicked.connect(self.copy_selected_transcription)
        copy_btn.setStyleSheet(self.get_secondary_button_style())

        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.clicked.connect(self.clear_all_transcriptions)
        clear_all_btn.setStyleSheet(self.get_secondary_button_style())

        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self.export_transcriptions)
        export_btn.setStyleSheet(self.get_secondary_button_style())

        button_layout.addWidget(copy_btn)
        button_layout.addWidget(clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(export_btn)

        layout.addWidget(self.transcriptions_list)
        layout.addLayout(button_layout)

    def get_secondary_button_style(self) -> str:
        """Get secondary button styling"""
        return f"""
            QPushButton {{
                background-color: {FlowColors.CARD_BG};
                color: {FlowColors.TEXT_PRIMARY};
                border: 1px solid {FlowColors.BORDER};
                border-radius: 6px;
                font-weight: 400;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {FlowColors.HOVER_BG};
            }}
            QPushButton:pressed {{
                background-color: {FlowColors.SIDEBAR_HOVER};
            }}
        """

    def update_transcriptions_list(self, sessions: List[RecordingSession]):
        """Update transcriptions list with session data"""
        self.transcriptions_list.clear()

        # Show only completed sessions with transcripts
        completed_sessions = [
            s for s in sessions if s.state == RecordingState.COMPLETED and s.transcript
        ]

        # Sort by start time (most recent first)
        completed_sessions.sort(key=lambda x: x.start_time, reverse=True)

        for session in completed_sessions[:10]:  # Show last 10
            timestamp = session.start_time.strftime("%H:%M:%S")
            preview = (
                session.transcript[:100] + "..."
                if len(session.transcript) > 100
                else session.transcript
            )
            item_text = f"[{timestamp}] {preview}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, session.transcript)
            self.transcriptions_list.addItem(item)

    def add_transcription(self, text: str):
        """Add a new transcription to the list"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        preview = text[:100] + "..." if len(text) > 100 else text
        item_text = f"[{timestamp}] {preview}"

        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, text)
        self.transcriptions_list.insertItem(0, item)

    def copy_selected_transcription(self):
        """Copy selected transcription to clipboard"""
        current_item = self.transcriptions_list.currentItem()
        if current_item:
            text = current_item.data(Qt.ItemDataRole.UserRole)
            if text:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                self.transcription_copied.emit("📋 Copied to clipboard")

    def clear_all_transcriptions(self):
        """Clear all transcriptions with confirmation"""
        if self.transcriptions_list.count() == 0:
            return

        reply = QMessageBox.question(
            self,
            "Clear All Transcriptions",
            "Are you sure you want to clear all transcriptions?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.transcriptions_list.clear()
            self.transcriptions_cleared.emit()

    def export_transcriptions(self):
        """Export transcriptions to file"""
        if self.transcriptions_list.count() == 0:
            QMessageBox.information(self, "Export", "No transcriptions to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Transcriptions",
            f"Transcriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;JSON Files (*.json);;All Files (*)",
        )

        if filename:
            try:
                transcriptions = []
                for i in range(self.transcriptions_list.count()):
                    item = self.transcriptions_list.item(i)
                    text = item.data(Qt.ItemDataRole.UserRole)
                    if text:
                        transcriptions.append(
                            {"timestamp": datetime.now().isoformat(), "text": text}
                        )

                if filename.endswith(".json"):
                    with open(filename, "w") as f:
                        json.dump(transcriptions, f, indent=2)
                else:
                    with open(filename, "w") as f:
                        for trans in transcriptions:
                            f.write(f"[{trans['timestamp']}] {trans['text']}\n\n")

                self.transcriptions_exported.emit(
                    f"💾 Exported to {os.path.basename(filename)}"
                )

            except Exception as e:
                QMessageBox.warning(
                    self, "Export Error", f"Could not save file: {str(e)}"
                )
