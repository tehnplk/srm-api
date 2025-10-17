import sys

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QApplication,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Setting_ui(object):
    """
    UI for MySQL connection settings with large, readable inputs.
    """

    def setupUi(self, Setting_ui):
        """
        Build Settings form.
        """
        # Window properties
        Setting_ui.setWindowTitle("ตั้งค่าการเชื่อมต่อ MySQL")
        Setting_ui.resize(900, 650)

        # Main layout
        self.main_layout = QVBoxLayout(Setting_ui)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(18)

        # Title
        self.title_label = QLabel("การตั้งค่าการเชื่อมต่อฐานข้อมูล MySQL", Setting_ui)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.title_label)

        # Group
        self.connection_group = QGroupBox("ข้อมูลการเชื่อมต่อ", Setting_ui)
        self.connection_group.setFont(QFont("Segoe UI", 11))
        self.main_layout.addWidget(self.connection_group)

        # Form
        self.form_layout = QFormLayout(self.connection_group)
        self.form_layout.setHorizontalSpacing(16)
        self.form_layout.setVerticalSpacing(12)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Helper for input style and sizing
        def apply_input_sizing(widget: QWidget):
            widget.setMinimumWidth(380)
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            widget.setFont(QFont("Segoe UI", 12))

        # Host
        self.host_edit = QLineEdit(Setting_ui)
        self.host_edit.setPlaceholderText("localhost")
        apply_input_sizing(self.host_edit)
        self.form_layout.addRow(QLabel("Host:"), self.host_edit)

        # Port
        self.port_spin = QSpinBox(Setting_ui)
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(3306)
        apply_input_sizing(self.port_spin)
        self.form_layout.addRow(QLabel("Port:"), self.port_spin)

        # Database
        self.database_edit = QLineEdit(Setting_ui)
        self.database_edit.setPlaceholderText("database_name")
        apply_input_sizing(self.database_edit)
        self.form_layout.addRow(QLabel("Database:"), self.database_edit)

        # Username
        self.username_edit = QLineEdit(Setting_ui)
        self.username_edit.setPlaceholderText("username")
        apply_input_sizing(self.username_edit)
        self.form_layout.addRow(QLabel("Username:"), self.username_edit)

        # Password
        self.password_edit = QLineEdit(Setting_ui)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("password")
        apply_input_sizing(self.password_edit)
        self.form_layout.addRow(QLabel("Password:"), self.password_edit)

        # Timeout
        self.timeout_spin = QSpinBox(Setting_ui)
        self.timeout_spin.setRange(1, 120)
        self.timeout_spin.setValue(10)
        apply_input_sizing(self.timeout_spin)
        self.form_layout.addRow(QLabel("Timeout (s):"), self.timeout_spin)

        # Buttons
        self.buttons = QHBoxLayout()
        self.buttons.setSpacing(10)

        def make_btn(text: str) -> QPushButton:
            btn = QPushButton(text, Setting_ui)
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
            btn.setMinimumWidth(140)
            return btn

        self.test_button = make_btn("ทดสอบการเชื่อมต่อ")
        self.save_button = make_btn("บันทึก")
        self.load_button = make_btn("โหลด")
        self.cancel_button = make_btn("ยกเลิก")

        self.buttons.addStretch(1)
        self.buttons.addWidget(self.test_button)
        self.buttons.addWidget(self.save_button)
        self.buttons.addWidget(self.load_button)
        self.buttons.addWidget(self.cancel_button)
        self.buttons.addStretch(1)

        self.main_layout.addLayout(self.buttons)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = Setting_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
