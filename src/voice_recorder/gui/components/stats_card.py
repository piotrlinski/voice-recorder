"""
Flow-style statistics card component.
"""

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtCore import pyqtProperty
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)

from .colors import FlowColors


class FlowStatCard(QWidget):
    """Flow-style statistics card with animations"""

    def __init__(self, icon, value, label, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Animation properties
        self._hover_elevation = 0.0
        self._entrance_opacity = 0.0

        # Create animations
        self.hover_animation = QPropertyAnimation(self, b"hover_elevation")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.entrance_animation = QPropertyAnimation(self, b"entrance_opacity")
        self.entrance_animation.setDuration(400)
        self.entrance_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setup_ui(icon, value, label, color)

        # Start entrance animation
        QTimer.singleShot(100, self.animate_entrance)

    @pyqtProperty(float)
    def hover_elevation(self):
        return self._hover_elevation

    @hover_elevation.setter
    def hover_elevation(self, elevation):
        self._hover_elevation = elevation
        self.update()

    @pyqtProperty(float)
    def entrance_opacity(self):
        return self._entrance_opacity

    @entrance_opacity.setter
    def entrance_opacity(self, opacity):
        self._entrance_opacity = opacity
        self.setWindowOpacity(opacity)

    def animate_entrance(self):
        """Animate card entrance"""
        self.entrance_animation.setStartValue(0.0)
        self.entrance_animation.setEndValue(1.0)
        self.entrance_animation.start()

    def enterEvent(self, event):
        """Animate hover enter"""
        self.hover_animation.setStartValue(self._hover_elevation)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Animate hover leave"""
        self.hover_animation.setStartValue(self._hover_elevation)
        self.hover_animation.setEndValue(0.0)
        self.hover_animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Custom paint with hover animation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw hover elevation effect
        if self._hover_elevation > 0:
            # Subtle lift effect with shadow
            shadow_offset = int(2 * self._hover_elevation)
            shadow_color = QColor(0, 0, 0, int(20 * self._hover_elevation))

            shadow_rect = self.rect().adjusted(0, shadow_offset, 0, shadow_offset)
            painter.fillRect(shadow_rect, shadow_color)

        super().paintEvent(event)

    def setup_ui(self, icon, value, label, color):
        """Setup the statistics card"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 18px;
            background-color: {color}20;
            border-radius: 6px;
        """
        )

        # Text container
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
        """
        )

        # Label
        label_label = QLabel(label)
        label_label.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_SECONDARY};
            font-size: 13px;
            font-weight: 400;
        """
        )

        text_layout.addWidget(self.value_label)
        text_layout.addWidget(label_label)

        layout.addWidget(icon_label)
        layout.addWidget(text_container)
        layout.addStretch()

    def update_value(self, new_value: str):
        """Update the card value"""
        self.value_label.setText(new_value)
