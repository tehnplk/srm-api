import sys

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QApplication,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QProgressBar


class Update_ui(object):
    """
    UI class following the scaffold pattern for management screens.
    """

    def setupUi(self, Update_ui):
        """Set up UI for the Update dialog (modern style)."""
        Update_ui.setWindowTitle("ตรวจสอบอัปเดต HisHelp")
        Update_ui.resize(640, 380)

        # Root layout on the provided widget/dialog
        self.main_layout = QVBoxLayout(Update_ui)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)

        # Title
        self.title_label = QLabel("อัปเดตโปรแกรม HisHelp", Update_ui)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.title_label)

        # Current version block
        cur_title = QLabel("เวอร์ชันปัจจุบัน", Update_ui)
        cur_font = QFont()
        cur_font.setPointSize(12)
        cur_font.setBold(True)
        cur_title.setFont(cur_font)
        self.main_layout.addWidget(cur_title)

        self.lbl_cur = QLabel("-", Update_ui)
        self.lbl_cur.setWordWrap(True)
        self.main_layout.addWidget(self.lbl_cur)

        # Spacer
        self.main_layout.addSpacing(6)

        # New version block
        new_title = QLabel("เวอร์ชันใหม่", Update_ui)
        new_title.setFont(cur_font)
        self.main_layout.addWidget(new_title)

        self.lbl_new = QLabel("ยังไม่ได้ตรวจสอบอัปเดต", Update_ui)
        self.lbl_new.setWordWrap(True)
        self.main_layout.addWidget(self.lbl_new)

        self.lbl_notes = QLabel("", Update_ui)
        self.lbl_notes.setWordWrap(True)
        self.lbl_notes.setStyleSheet("color:#555; font-size: 12px;")
        self.main_layout.addWidget(self.lbl_notes)

        # Status and progress
        self.lbl_status = QLabel("พร้อมตรวจสอบอัปเดต", Update_ui)
        self.lbl_status.setStyleSheet("color:#2c3e50; font-weight: bold;")
        self.main_layout.addWidget(self.lbl_status)

        self.progress = QProgressBar(Update_ui)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet(
            "QProgressBar {height: 18px; border: 1px solid #bdc3c7; border-radius: 6px; background: #ecf0f1;}"
            "QProgressBar::chunk {background-color: #27ae60; border-radius: 6px;}"
        )
        self.main_layout.addWidget(self.progress)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.btn_check = QPushButton("🔄 ตรวจสอบอัปเดต", Update_ui)
        self.btn_open = QPushButton("⬇️ ดาวน์โหลดและติดตั้ง", Update_ui)
        # Button styles
        btn_style = (
            "QPushButton { background-color: #3498db; color: white; border: none; padding: 10px 18px;"
            " border-radius: 6px; font-weight: 600; font-size: 14px; }"
            "QPushButton:hover { background-color: #2980b9; }"
            "QPushButton:disabled { background-color: #95a5a6; }"
        )
        self.btn_check.setStyleSheet(btn_style)
        self.btn_open.setStyleSheet(btn_style.replace('#3498db', '#2ecc71').replace('#2980b9', '#27ae60'))
        btn_row.addWidget(self.btn_check)
        btn_row.addWidget(self.btn_open)
        self.main_layout.addLayout(btn_row)

    def retranslateUi(self, Update_ui):
        """
        Retranslate the user interface.
        """
        Update_ui.setWindowTitle("ตรวจสอบอัปเดต HisHelp")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = Update_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
