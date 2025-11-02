# -*- coding: utf-8 -*-

"""
Login UI Module
Dummy implementation for login interface
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QGridLayout,
    QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QPixmap, QPainter, QLinearGradient, QColor


class Login_ui(QWidget):
    """
    Login UI class - dummy implementation
    """
    
    # Signal for successful login
    login_successful = pyqtSignal(str)
    login_failed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        
    def setupUi(self):
        """
        Setup login interface
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create login container
        self.create_login_container()
        main_layout.addWidget(self.login_container, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Set window properties
        self.setMinimumSize(400, 500)
        self.setWindowTitle("เข้าสู่ระบบ SRM API")
        
    def create_login_container(self):
        """
        Create main login container with improved styling
        """
        self.login_container = QFrame()
        self.login_container.setFixedSize(380, 420)
        self.login_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
            }
        """)
        
        layout = QVBoxLayout(self.login_container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # Logo/Title section
        self.create_header_section(layout)
        
        # Form section
        self.create_form_section(layout)
        
        # Login button
        self.create_login_button(layout)
        
        # Footer section
        self.create_footer_section(layout)
        
    def create_header_section(self, layout):
        """
        Create header with title only (no image)
        """
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        self.title_label = QLabel("SRM API")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px 0 10px 0;
            }
        """)
        
        # Subtitle
        self.subtitle_label = QLabel("ระบบจัดการข้อมูลประชากรและผู้รับบริการ")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 30px;
            }
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        
        layout.addLayout(header_layout)
        
    def create_form_section(self, layout):
        """
        Create login form fields with improved styling
        """
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Username field
        self.username_label = QLabel("ชื่อผู้ใช้")
        self.username_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #2c3e50;
                font-weight: 600;
                margin-bottom: 5px;
            }
        """)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("กรอกชื่อผู้ใช้")
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """)
        
        # Password field
        self.password_label = QLabel("รหัสผ่าน")
        self.password_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #2c3e50;
                font-weight: 600;
                margin-bottom: 5px;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("กรอกรหัสผ่าน")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("จดจำฉัน")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #e1e8ed;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
        
        # Add widgets to form
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_checkbox)
        
        layout.addLayout(form_layout)
        
    def create_login_button(self, layout):
        """
        Create login button with improved styling
        """
        self.login_button = QPushButton("เข้าสู่ระบบ")
        self.login_button.setFixedHeight(48)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #ecf0f1;
            }
        """)
        
        layout.addWidget(self.login_button)
        
    def create_footer_section(self, layout):
        """
        Create footer with additional options
        """
        footer_layout = QVBoxLayout()
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.setSpacing(12)
        
        # Forgot password
        self.forgot_password_label = QLabel("ลืมรหัสผ่าน?")
        self.forgot_password_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 13px;
                text-decoration: underline;
            }
        """)
        self.forgot_password_label.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Version info
        self.version_label = QLabel("เวอร์ชัน 1.0.0")
        self.version_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 11px;
            }
        """)
        
        footer_layout.addWidget(self.forgot_password_label)
        footer_layout.addWidget(self.version_label)
        
        layout.addLayout(footer_layout)
        
        # Add stretch to push footer to bottom
        layout.addStretch()
        
    def get_username(self):
        """Get username from input field"""
        return self.username_input.text().strip()
        
    def get_password(self):
        """Get password from input field"""
        return self.password_input.text()
        
    def is_remember_me(self):
        """Check if remember me is checked"""
        return self.remember_checkbox.isChecked()
        
    def clear_fields(self):
        """Clear all input fields"""
        self.username_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
        
    def set_error_message(self, message):
        """Set error message (dummy implementation)"""
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #fdf2f2;
                color: #2c3e50;
            }
        """)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #fdf2f2;
                color: #2c3e50;
            }
        """)
        
    def clear_error_message(self):
        """Clear error styling"""
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """)
