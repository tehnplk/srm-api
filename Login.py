# -*- coding: utf-8 -*-

"""
Login Module
Dummy implementation for login functionality
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import pyqtSlot, QTimer
from Login_ui import Login_ui


class Login(Login_ui):
    """
    Login class - dummy implementation
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_connections()
        self.attempts = 0
        self.max_attempts = 3
        
    def setup_connections(self):
        """
        Setup signal connections
        """
        self.login_button.clicked.connect(self.attempt_login)
        self.forgot_password_label.mousePressEvent = self.on_forgot_password
        
        # Enter key support
        self.username_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)
        
        # Clear error on input change
        self.username_input.textChanged.connect(self.clear_error_message)
        self.password_input.textChanged.connect(self.clear_error_message)
        
    @pyqtSlot()
    def attempt_login(self):
        """
        Attempt to login - dummy implementation
        """
        username = self.get_username()
        password = self.get_password()
        
        # Validate input
        if not username or not password:
            QMessageBox.warning(self, "คำเตือน", "กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
            return
            
        # Dummy authentication
        if self.dummy_authenticate(username, password):
            self.login_successful.emit(username)
            QMessageBox.information(self, "สำเร็จ", f"เข้าสู่ระบบสำเร็จ!\nยินดีต้อนรับ {username}")
        else:
            self.attempts += 1
            remaining_attempts = self.max_attempts - self.attempts
            
            if remaining_attempts > 0:
                self.set_error_message("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
                QMessageBox.warning(
                    self, 
                    "ผิดพลาด", 
                    f"ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง\nคงเหลือ {remaining_attempts} ครั้ง"
                )
            else:
                QMessageBox.critical(
                    self, 
                    "ถูกบล็อก", 
                    "คุณพยายามเข้าสู่ระบบผิดพลาดเกินขีดจำกัด\nกรุณาลองใหม่ภายหลัง"
                )
                self.login_button.setEnabled(False)
                QTimer.singleShot(5000, self.enable_login_button)  # Enable after 5 seconds
                
    def dummy_authenticate(self, username, password):
        """
        Dummy authentication function
        Returns True for demo credentials
        """
        # Demo credentials
        demo_users = {
            "admin": "1234",
            "user": "password",
            "test": "test",
            "demo": "demo"
        }
        
        return demo_users.get(username) == password
        
    def enable_login_button(self):
        """
        Re-enable login button after timeout
        """
        self.login_button.setEnabled(True)
        self.attempts = 0
        self.clear_fields()
        self.clear_error_message()
        
    def on_forgot_password(self, event):
        """
        Handle forgot password click - dummy implementation
        """
        QMessageBox.information(
            self,
            "ลืมรหัสผ่าน",
            "ติดต่อผู้ดูแลระบบเพื่อรับรหัสผ่านใหม่\n\n"
            "Email: admin@srm-api.com\n"
            "Tel: 02-123-4567"
        )
        
    def reset_login_form(self):
        """
        Reset login form to initial state
        """
        self.clear_fields()
        self.clear_error_message()
        self.attempts = 0
        self.login_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create login window
    login_window = Login()
    login_window.show()
    
    sys.exit(app.exec())
