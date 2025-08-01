"""
Icon generation utilities for the voice recorder application.
"""

try:
    from PyQt6.QtGui import (
        QIcon,
        QPixmap,
        QPainter,
        QPen,
        QBrush,
        QColor,
        QFont,
        QRadialGradient,
        QLinearGradient,
        QPainterPath,
    )
    from PyQt6.QtCore import Qt, QRect, QPoint, QPointF
except ImportError:
    print("PyQt6 not installed. Run: pip install PyQt6")
    exit(1)


class VoiceRecorderIcons:
    """Generate icons for different application states"""

    @staticmethod
    def create_app_icon(size: int = 64) -> QIcon:
        """Create the main application icon with a smiling microphone"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background circle with gradient effect
        gradient = QRadialGradient(size // 2, size // 2, size // 2)
        gradient.setColorAt(0, QColor("#4285F4"))
        gradient.setColorAt(1, QColor("#3367D6"))

        painter.setPen(QPen(QColor("#2C5AA0"), 1))
        painter.setBrush(QBrush(gradient))

        margin = 2
        painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)

        # Microphone body (larger and more detailed)
        mic_gradient = QLinearGradient(0, size // 4, 0, size // 2)
        mic_gradient.setColorAt(0, QColor("#FFFFFF"))
        mic_gradient.setColorAt(1, QColor("#F8F9FA"))

        painter.setPen(QPen(QColor("#E8EAED"), 1))
        painter.setBrush(QBrush(mic_gradient))

        mic_width = size // 5  # Larger microphone
        mic_height = size // 3
        mic_x = (size - mic_width) // 2
        mic_y = size // 4

        painter.drawRoundedRect(
            mic_x, mic_y, mic_width, mic_height, mic_width // 2, mic_width // 2
        )

        # Microphone grille lines
        grille_color = QColor("#BDC1C6")
        painter.setPen(QPen(grille_color, 1))

        for i in range(5):
            y_pos = mic_y + mic_height // 6 + i * (mic_height // 8)
            painter.drawLine(mic_x + 2, y_pos, mic_x + mic_width - 2, y_pos)

        # Microphone stand
        stand_color = QColor(255, 255, 255, 230)
        painter.setPen(QPen(stand_color, 2))
        painter.setBrush(QBrush(stand_color))

        stand_y = mic_y + mic_height
        stand_bottom = size - size // 5
        painter.drawLine(size // 2, stand_y, size // 2, stand_bottom)

        # Stand base (rounded)
        base_width = mic_width + 2
        base_height = 3
        base_x = size // 2 - base_width // 2
        painter.drawRoundedRect(
            base_x,
            stand_bottom,
            base_width,
            base_height,
            base_height // 2,
            base_height // 2,
        )

        # Happy face on microphone
        face_color = QColor("#4285F4")
        painter.setPen(QPen(face_color, 2))
        painter.setBrush(QBrush(face_color))

        # Eyes (slightly larger)
        eye_size = max(2, size // 20)
        left_eye_x = mic_x + mic_width // 3 - eye_size // 2
        right_eye_x = mic_x + 2 * mic_width // 3 - eye_size // 2
        eye_y = mic_y + mic_height // 4

        painter.drawEllipse(left_eye_x, eye_y, eye_size, eye_size)
        painter.drawEllipse(right_eye_x, eye_y, eye_size, eye_size)

        # Smile (more prominent)
        painter.setPen(QPen(face_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        smile_rect = QRect(
            mic_x + mic_width // 6,
            mic_y + mic_height // 2,
            2 * mic_width // 3,
            mic_width // 3,
        )
        painter.drawArc(smile_rect, 0, 16 * 180)

        # Sound waves (more stylized)
        wave_color = QColor(255, 255, 255, 150)
        painter.setPen(QPen(wave_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Left waves
        wave1_start = QPointF(size // 6, size // 3)
        wave1_end = QPointF(size // 6, 2 * size // 3)
        wave1_control = QPointF(size // 8, size // 2)

        path1 = QPainterPath()
        path1.moveTo(wave1_start)
        path1.quadTo(wave1_control, wave1_end)
        painter.drawPath(path1)

        wave2_start = QPointF(size // 4, size // 2 - size // 8)
        wave2_end = QPointF(size // 4, size // 2 + size // 8)
        wave2_control = QPointF(size // 5, size // 2)

        path2 = QPainterPath()
        path2.moveTo(wave2_start)
        path2.quadTo(wave2_control, wave2_end)
        painter.drawPath(path2)

        # Right waves
        wave3_start = QPointF(5 * size // 6, size // 3)
        wave3_end = QPointF(5 * size // 6, 2 * size // 3)
        wave3_control = QPointF(7 * size // 8, size // 2)

        path3 = QPainterPath()
        path3.moveTo(wave3_start)
        path3.quadTo(wave3_control, wave3_end)
        painter.drawPath(path3)

        wave4_start = QPointF(3 * size // 4, size // 2 - size // 8)
        wave4_end = QPointF(3 * size // 4, size // 2 + size // 8)
        wave4_control = QPointF(4 * size // 5, size // 2)

        path4 = QPainterPath()
        path4.moveTo(wave4_start)
        path4.quadTo(wave4_control, wave4_end)
        painter.drawPath(path4)

        # Subtle highlight on microphone
        highlight_color = QColor(255, 255, 255, 100)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(highlight_color))

        highlight_x = mic_x + mic_width // 4
        highlight_y = mic_y + 2
        highlight_width = mic_width // 2
        highlight_height = 2

        painter.drawEllipse(highlight_x, highlight_y, highlight_width, highlight_height)

        painter.end()
        return QIcon(pixmap)

    @staticmethod
    def create_tray_icon(color: str, size: int = 32) -> QIcon:
        """Create a system tray icon with specified color"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background circle
        bg_color = QColor(color)
        painter.setPen(QPen(bg_color.darker(120), 2))
        painter.setBrush(QBrush(bg_color))

        margin = 2
        painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)

        # Microphone symbol
        mic_color = QColor(255, 255, 255)
        painter.setPen(QPen(mic_color, 2))
        painter.setBrush(QBrush(mic_color))

        # Simplified microphone
        mic_width = size // 6
        mic_height = size // 3
        mic_x = (size - mic_width) // 2
        mic_y = size // 4

        painter.drawRoundedRect(
            mic_x, mic_y, mic_width, mic_height, mic_width // 2, mic_width // 2
        )

        # Stand
        painter.drawLine(size // 2, mic_y + mic_height, size // 2, size - size // 4)
        base_width = size // 3
        base_x = size // 2 - base_width // 2
        painter.drawLine(
            base_x, size - size // 4, base_x + base_width, size - size // 4
        )

        painter.end()
        return QIcon(pixmap)

    @staticmethod
    def create_ready_icon(size: int = 32) -> QIcon:
        """Create green 'ready' tray icon"""
        return VoiceRecorderIcons.create_tray_icon("#34A853", size)

    @staticmethod
    def create_recording_icon(size: int = 32) -> QIcon:
        """Create red 'recording' tray icon"""
        return VoiceRecorderIcons.create_tray_icon("#EA4335", size)

    @staticmethod
    def create_processing_icon(size: int = 32) -> QIcon:
        """Create orange 'processing' tray icon"""
        return VoiceRecorderIcons.create_tray_icon("#FF9800", size)

    @staticmethod
    def create_error_icon(size: int = 32) -> QIcon:
        """Create gray 'error' tray icon"""
        return VoiceRecorderIcons.create_tray_icon("#9AA0A6", size)
