import sys
import os

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QTableView,
    QHBoxLayout,
    QDateEdit,
    QApplication,
    QPushButton,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont


class PatientToday_ui(object):
    """
    UI class for today's checked patients view.
    """

    def setupUi(self, PatientToday_ui):
        """
        Set up the user interface.
        """
        # Set window properties
        PatientToday_ui.setWindowTitle("ผู้รับบริการวันนี้")
        PatientToday_ui.resize(1000, 700)

        # Create main layout
        self.main_layout = QVBoxLayout(PatientToday_ui)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Create title label
        self.title_label = QLabel("ผู้รับบริการวันนี้", PatientToday_ui)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;"
        )
        self.main_layout.addWidget(self.title_label)

        # Top bar layout (Patient-like) + keep date picker
        self.top_bar = QHBoxLayout()
        self.top_bar.setSpacing(8)

        # Date picker (kept)
        self.date_label = QLabel("วันที่:", PatientToday_ui)
        self.top_bar.addWidget(self.date_label)

        self.date_edit = QDateEdit(PatientToday_ui)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        try:
            self.date_edit.setFixedHeight(32)
            self.date_edit.setMinimumWidth(140)
            self.date_edit.setFont(QFont("Segoe UI", 11))
        except Exception:
            pass
        try:
            cal = self.date_edit.calendarWidget()
            if cal is not None:
                cal.setStyleSheet(
                    """
                    QCalendarWidget QToolButton { color: #000000; }
                    QCalendarWidget QSpinBox { color: #000000; }
                    QCalendarWidget QComboBox { color: #000000; }
                    """
                )
        except Exception:
            pass
        self.top_bar.addWidget(self.date_edit)

        # Buttons (same as Patient)
        self.refresh_button = QPushButton("🔄 Refresh Token", PatientToday_ui)
        self.refresh_button.setMinimumWidth(140)
        self.refresh_button.setFont(QFont("Segoe UI", 11))
        self.top_bar.addWidget(self.refresh_button)

        self.check_rights_button = QPushButton("✅ ตรวจสอบสิทธิ", PatientToday_ui)
        self.check_rights_button.setMinimumWidth(160)
        self.check_rights_button.setFont(QFont("Segoe UI", 11))
        self.top_bar.addWidget(self.check_rights_button)

        self.stop_rights_button = QPushButton("⏹ หยุดตรวจสอบสิทธิ", PatientToday_ui)
        self.stop_rights_button.setMinimumWidth(180)
        self.stop_rights_button.setFont(QFont("Segoe UI", 11))
        self.top_bar.addWidget(self.stop_rights_button)

        self.top_bar.addStretch(1)
        self.main_layout.addLayout(self.top_bar)

        # Table view (same name as Patient)
        self.table = QTableView(PatientToday_ui)
        self.table.setFont(QFont("Segoe UI", 11))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        try:
            self.table.setStyleSheet(
                "QTableView::item:selected{background:#FFE5B4;color:black;}"
                "QTableView::item:selected:active{background:#FFE5B4;color:black;}"
                "QTableView::item:selected:!active{background:#FFE5B4;color:black;}"
            )
        except Exception:
            pass
        self.main_layout.addWidget(self.table)

        # Backward compatibility: expose visit_table alias
        self.visit_table = self.table

    def retranslateUi(self, PatientToday_ui):
        PatientToday_ui.setWindowTitle("ผู้รับบริการวันนี้")
        self.title_label.setText("ผู้รับบริการวันนี้")
        self.date_label.setText("วันที่:")
        self.check_rights_button.setText("✅ ตรวจสอบสิทธิ")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = PatientToday_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
