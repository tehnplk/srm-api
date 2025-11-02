import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QProgressBar, QTextEdit, QGroupBox, QCheckBox, QFileDialog,
    QApplication, QScrollArea, QFrame, QGridLayout, QSpinBox,
    QDateEdit, QComboBox
)
from PyQt6.QtCore import Qt, QDate, QLocale
from PyQt6.QtGui import QFont


class Export16Files_ui(object):
    """
    UI class for exporting 16 files module.
    """

    def setupUi(self, Export16Files):
        """
        Set up the user interface for exporting 16 files.
        """
        # Set window properties
        Export16Files.setWindowTitle("ส่งออก 16 แฟ้ม")
        Export16Files.resize(1200, 800)
        Export16Files.setMinimumSize(1000, 600)

        # Create main layout
        self.main_layout = QVBoxLayout(Export16Files)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Create title label
        self.title_label = QLabel("ส่งออกข้อมูล 16 แฟ้ม", Export16Files)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;"
        )
        self.main_layout.addWidget(self.title_label)

        # Create scroll area for content
        self.scroll_area = QScrollArea(Export16Files)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """
        )

        # Create scroll widget
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(15)

        # Create settings group
        self.settings_group = QGroupBox("การตั้งค่าการส่งออก", self.scroll_widget)
        self.settings_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )
        self.settings_layout = QGridLayout(self.settings_group)

        # Date range selection
        self.start_date_label = QLabel("วันที่เริ่มต้น:", self.settings_group)
        self.start_date_label.setStyleSheet("font-weight: normal; color: #34495e;")
        self.settings_layout.addWidget(self.start_date_label, 0, 0)

        self.start_date = QDateEdit(self.settings_group)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        # Set English locale to avoid Thai numerals
        self.start_date.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.start_date.setStyleSheet(
            """
            QDateEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
        """
        )
        self.settings_layout.addWidget(self.start_date, 0, 1)

        self.end_date_label = QLabel("วันที่สิ้นสุด:", self.settings_group)
        self.end_date_label.setStyleSheet("font-weight: normal; color: #34495e;")
        self.settings_layout.addWidget(self.end_date_label, 0, 2)

        self.end_date = QDateEdit(self.settings_group)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        # Set English locale to avoid Thai numerals
        self.end_date.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.end_date.setStyleSheet(
            """
            QDateEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
        """
        )
        self.settings_layout.addWidget(self.end_date, 0, 3)

        # Export path selection
        self.export_path_label = QLabel("ที่เก็บไฟล์:", self.settings_group)
        self.export_path_label.setStyleSheet("font-weight: normal; color: #34495e;")
        self.settings_layout.addWidget(self.export_path_label, 1, 0)

        self.export_path_edit = QLabel(self.settings_group)
        self.export_path_edit.setText(os.path.expanduser("~/Desktop"))
        self.export_path_edit.setStyleSheet(
            """
            QLabel {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
        """
        )
        self.settings_layout.addWidget(self.export_path_edit, 1, 1, 1, 2)

        self.browse_button = QPushButton("เลือกโฟลเดอร์", self.settings_group)
        self.browse_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        )
        self.settings_layout.addWidget(self.browse_button, 1, 3)

        # File format selection
        self.format_label = QLabel("รูปแบบไฟล์:", self.settings_group)
        self.format_label.setStyleSheet("font-weight: normal; color: #34495e;")
        self.settings_layout.addWidget(self.format_label, 2, 0)

        self.format_combo = QComboBox(self.settings_group)
        self.format_combo.addItems(["CSV", "Excel (.xlsx)", "Text (.txt)"])
        self.format_combo.setStyleSheet(
            """
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #34495e;
            }
        """
        )
        self.settings_layout.addWidget(self.format_combo, 2, 1)

        self.scroll_layout.addWidget(self.settings_group)

        # Create files selection group
        self.files_group = QGroupBox("เลือกแฟ้มที่ต้องการส่งออก", self.scroll_widget)
        self.files_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )
        self.files_layout = QGridLayout(self.files_group)

        # Create checkboxes for 16 files
        self.file_checkboxes = []
        file_names = [
            "แฟ้มข้อมูลผู้ป่วย (Patient)",
            "แฟ้มการรับบริการ (Admission)",
            "แฟ้มการวินิจฉัย (Diagnosis)",
            "แฟ้มการผ่าตัด (Surgery)",
            "แฟ้มยาและเวชภัณฑ์ (Medication)",
            "แฟ้มบริการพยาธิวิทยา (Pathology)",
            "แฟ้มบริการรังสีวิทยา (Radiology)",
            "แฟ้มการจำหน่าย (Discharge)",
            "แฟ้มแพทย์ (Doctor)",
            "แฟ้มพยาบาล (Nurse)",
            "แฟ้มห้องยา (Pharmacy)",
            "แฟ้มห้องปฏิบัติการ (Laboratory)",
            "แฟ้มค่าใช้จ่าย (Charges)",
            "แฟ้มการเยี่ยมไข้ (Visit)",
            "แฟ้มการส่งต่อ (Referral)",
            "แฟ้มสรุปรายวัน (Daily Summary)"
        ]

        # Select all checkbox
        self.select_all_checkbox = QCheckBox("เลือกทั้งหมด", self.files_group)
        self.select_all_checkbox.setStyleSheet(
            """
            QCheckBox {
                font-weight: bold;
                color: #2c3e50;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """
        )
        self.files_layout.addWidget(self.select_all_checkbox, 0, 0, 1, 2)

        # Individual file checkboxes
        for i, file_name in enumerate(file_names):
            checkbox = QCheckBox(file_name, self.files_group)
            checkbox.setChecked(True)
            checkbox.setStyleSheet(
                """
                QCheckBox {
                    color: #34495e;
                    font-size: 12px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """
            )
            row = (i // 2) + 1
            col = i % 2
            self.files_layout.addWidget(checkbox, row, col)
            self.file_checkboxes.append(checkbox)

        self.scroll_layout.addWidget(self.files_group)

        # Create progress group
        self.progress_group = QGroupBox("สถานะการส่งออก", self.scroll_widget)
        self.progress_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #e67e22;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )
        self.progress_layout = QVBoxLayout(self.progress_group)

        # Progress bar
        self.progress_bar = QProgressBar(self.progress_group)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
                color: #2c3e50;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """
        )
        self.progress_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("พร้อมส่งออกข้อมูล", self.progress_group)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #27ae60; font-weight: bold; font-size: 13px;"
        )
        self.progress_layout.addWidget(self.status_label)

        # Log text area
        self.log_text = QTextEdit(self.progress_group)
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """
        )
        self.progress_layout.addWidget(self.log_text)

        self.scroll_layout.addWidget(self.progress_group)

        # Set scroll widget
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

        # Create button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()

        # Export button
        self.export_button = QPushButton("ส่งออกข้อมูล", Export16Files)
        self.export_button.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
        """
        )
        self.button_layout.addWidget(self.export_button)

        # Cancel button
        self.cancel_button = QPushButton("ยกเลิก", Export16Files)
        self.cancel_button.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """
        )
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(self.button_layout)

    def retranslateUi(self, Export16Files):
        """
        Retranslate the user interface.
        """
        Export16Files.setWindowTitle("ส่งออก 16 แฟ้ม")
        self.title_label.setText("ส่งออกข้อมูล 16 แฟ้ม")
        self.settings_group.setTitle("การตั้งค่าการส่งออก")
        self.files_group.setTitle("เลือกแฟ้มที่ต้องการส่งออก")
        self.progress_group.setTitle("สถานะการส่งออก")
        self.export_button.setText("ส่งออกข้อมูล")
        self.cancel_button.setText("ยกเลิก")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = Export16Files_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
