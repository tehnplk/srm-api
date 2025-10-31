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
from PyQt6.QtGui import QIcon


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

        # Create date picker layout
        self.date_layout = QHBoxLayout()

        self.date_label = QLabel("วันที่:", PatientToday_ui)
        self.date_layout.addWidget(self.date_label)

        self.date_edit = QDateEdit(PatientToday_ui)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        try:
            self.date_edit.setFixedHeight(44)
            self.date_edit.setMinimumWidth(180)
            self.date_edit.setStyleSheet("font-size: 18px; padding: 6px 12px;")
        except Exception:
            pass
        # Style calendar popup: make month/year selectors black
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
        self.date_layout.addWidget(self.date_edit)

        # Add check rights button
        self.check_rights_button = QPushButton("ตรวจสอบสิทธิ", PatientToday_ui)
        icon_path = os.path.join(os.path.dirname(__file__), "check.png")
        self.check_rights_button.setIcon(QIcon(icon_path))
        self.check_rights_button.setIconSize(QSize(20, 20))
        self.date_layout.addWidget(self.check_rights_button)

        # Push contents to the left
        self.date_layout.addStretch()

        # Add date layout to main layout
        self.main_layout.addLayout(self.date_layout)

        # Create table view
        self.visit_table = QTableView(PatientToday_ui)
        self.main_layout.addWidget(self.visit_table)

    def retranslateUi(self, PatientToday_ui):
        PatientToday_ui.setWindowTitle("ผู้รับบริการวันนี้")
        self.title_label.setText("ผู้รับบริการวันนี้")
        self.date_label.setText("วันที่:")
        self.check_rights_button.setText("ตรวจสอบสิทธิ")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = PatientToday_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
