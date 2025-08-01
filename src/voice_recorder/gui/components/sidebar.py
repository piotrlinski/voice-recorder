"""
Flow-style sidebar components.
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


class FlowSidebarItem(QPushButton):
    """Flow-style sidebar navigation item with animations"""

    def __init__(self, icon_text, text, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.item_text = text
        self.setMinimumHeight(36)
        self.setMaximumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Animation properties
        self._hover_opacity = 0.0
        self._selection_scale = 1.0

        # Create animations
        self.hover_animation = QPropertyAnimation(self, b"hover_opacity")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.scale_animation = QPropertyAnimation(self, b"selection_scale")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setup_ui()

    @pyqtProperty(float)
    def hover_opacity(self):
        return self._hover_opacity

    @hover_opacity.setter
    def hover_opacity(self, opacity):
        self._hover_opacity = opacity
        self.update()

    @pyqtProperty(float)
    def selection_scale(self):
        return self._selection_scale

    @selection_scale.setter
    def selection_scale(self, scale):
        self._selection_scale = scale
        self.update()

    def enterEvent(self, event):
        """Animate on hover enter"""
        self.hover_animation.setStartValue(self._hover_opacity)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Animate on hover leave"""
        if not self.property("selected") == "true":
            self.hover_animation.setStartValue(self._hover_opacity)
            self.hover_animation.setEndValue(0.0)
            self.hover_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Add press animation"""
        self.scale_animation.setStartValue(self._selection_scale)
        self.scale_animation.setEndValue(0.95)
        self.scale_animation.setDuration(100)
        self.scale_animation.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Add release animation"""
        self.scale_animation.setStartValue(self._selection_scale)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.setDuration(200)
        self.scale_animation.start()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Custom paint with animation support"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Scale transform
        if self._selection_scale != 1.0:
            painter.save()
            center = self.rect().center()
            painter.translate(center)
            painter.scale(self._selection_scale, self._selection_scale)
            painter.translate(-center)

        # Draw background with animated hover
        if self._hover_opacity > 0 and not self.property("selected") == "true":
            hover_color = QColor(FlowColors.SIDEBAR_HOVER)
            hover_color.setAlphaF(self._hover_opacity)
            painter.fillRect(self.rect(), hover_color)

        # Draw selection background
        if self.property("selected") == "true":
            painter.fillRect(self.rect(), QColor(FlowColors.SIDEBAR_SELECTED))

        if self._selection_scale != 1.0:
            painter.restore()

        # Let the default paint handle the rest
        super().paintEvent(event)

    def setup_ui(self):
        """Setup the sidebar item appearance"""
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)

        # Icon label
        self.icon_label = QLabel(self.icon_text)
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_SECONDARY};
            font-size: 16px;
        """
        )

        # Text label
        self.text_label = QLabel(self.item_text)
        self.text_label.setStyleSheet(
            f"""
            color: {FlowColors.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: 400;
        """
        )

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        # Style the button
        self.setStyleSheet(
            f"""
            FlowSidebarItem {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                text-align: left;
            }}
            FlowSidebarItem:hover {{
                background-color: {FlowColors.SIDEBAR_HOVER};
            }}
            FlowSidebarItem[selected="true"] {{
                background-color: {FlowColors.SIDEBAR_SELECTED};
            }}
        """
        )

    def set_selected(self, selected):
        """Set selection state"""
        self.setProperty("selected", str(selected).lower())
        if selected:
            self.icon_label.setStyleSheet(
                f"""
                color: {FlowColors.ACCENT_BLUE};
                font-size: 16px;
            """
            )
            self.text_label.setStyleSheet(
                f"""
                color: {FlowColors.ACCENT_BLUE};
                font-size: 14px;
                font-weight: 500;
            """
            )
        else:
            self.icon_label.setStyleSheet(
                f"""
                color: {FlowColors.TEXT_SECONDARY};
                font-size: 16px;
            """
            )
            self.text_label.setStyleSheet(
                f"""
                color: {FlowColors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 400;
            """
            )
        self.style().unpolish(self)
        self.style().polish(self)
