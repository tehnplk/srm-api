from PyQt6.QtWidgets import QMdiArea
from PyQt6.QtGui import QPainter, QFont, QColor
from PyQt6.QtCore import Qt
from mainConfig import MAIN_CONFIG
class WatermarkMdiArea(QMdiArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.watermark_text = f"ParaCheck v{MAIN_CONFIG['version_name']}"
        self.watermark_color = QColor(200, 200, 200, 80)  # Light gray with transparency
        self.background_color = "#D2E2C3"  # Default light green
        self.set_background_color(self.background_color)
        
    def set_watermark(self, text, color=None):
        """Set custom watermark text and color"""
        self.watermark_text = text
        if color:
            # Convert string color to QColor if needed
            if isinstance(color, str):
                self.watermark_color = QColor(color)
            else:
                self.watermark_color = color
        self.update()
        
    def set_background_color(self, color):
        """Set the background color of the MDI area"""
        self.background_color = color
        self.setStyleSheet(f"""
            QMdiArea {{
                background-color: {color};
                background-image: none;
            }}
        """)
        self.update()
        
    def change_theme(self, theme_name):
        """Change to predefined color themes"""
        themes = {
            "default": "#d4f0ff",      # Light blue
            "blue": "#b3d9ff",         # Deep blue
            "green": "#d4ffd4",        # Light green
            "purple": "#e6d4ff",       # Light purple
            "orange": "#ffe6d4",       # Light orange
            "pink": "#ffd4e6",         # Light pink
            "yellow": "#ffffd4",       # Light yellow
            "gray": "#e8e8e8",         # Light gray
            "dark": "#404040",         # Dark theme
            "white": "#ffffff"         # White
        }
        
        if theme_name in themes:
            self.set_background_color(themes[theme_name])
        else:
            print(f"Theme '{theme_name}' not found. Available themes: {list(themes.keys())}")
    
    def paintEvent(self, event):
        """Override paint event to draw watermark"""
        super().paintEvent(event)
        
        # Only draw watermark if there are no sub-windows or they don't cover the entire area
        if len(self.subWindowList()) == 0:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Set font for watermark
            font = QFont("Arial", 48, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(self.watermark_color)
            
            # Calculate text position (center of the area)
            rect = self.viewport().rect()
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.watermark_text)
            
            # Add subtitle
            subtitle_font = QFont("Arial", 16)
            painter.setFont(subtitle_font)
            subtitle_color = QColor(150, 150, 150, 60)
            painter.setPen(subtitle_color)
            
            # Position subtitle below main text
            subtitle_rect = rect
            subtitle_rect.setTop(rect.center().y() + 30)
            painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, 
                           "Data Quality Management System")
            
            painter.end()
