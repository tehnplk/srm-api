import sys

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QApplication,
    QHBoxLayout,
    QPushButton,
    QTableView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Patient_ui(object):
    """
    UI for displaying patient list in a table with a refresh button.
    """

    def setupUi(self, Patient_ui):
        # Window properties
        Patient_ui.setWindowTitle("รายชื่อผู้ป่วย")
        Patient_ui.resize(1000, 700)

        # Main layout
        self.main_layout = QVBoxLayout(Patient_ui)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(10)

        # Top controls
        self.top_bar = QHBoxLayout()
        self.top_bar.setSpacing(8)

        self.refresh_button = QPushButton("Refresh Token", Patient_ui)
        self.refresh_button.setMinimumWidth(140)
        self.refresh_button.setFont(QFont("Segoe UI", 11))
        self.top_bar.addWidget(self.refresh_button)

        self.check_rights_button = QPushButton("ตรวจสอบสิทธิ", Patient_ui)
        self.check_rights_button.setMinimumWidth(160)
        self.check_rights_button.setFont(QFont("Segoe UI", 11))
        self.top_bar.addWidget(self.check_rights_button)

        self.top_bar.addStretch(1)
        self.main_layout.addLayout(self.top_bar)

        # Table view
        self.table = QTableView(Patient_ui)
        self.table.setFont(QFont("Segoe UI", 11))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.table)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = Patient_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
