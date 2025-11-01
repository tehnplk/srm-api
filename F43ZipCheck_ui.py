import sys
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTableView,
    QLineEdit,
    QGroupBox,
    QFormLayout,
    QSplitter,
    QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class F43ZipCheck_ui(object):
    def setupUi(self, F43ZipCheck_ui):
        F43ZipCheck_ui.setWindowTitle("ตรวจสอบ43แฟ้ม (ZIP)")
        F43ZipCheck_ui.resize(1000, 700)

        self.main_layout = QVBoxLayout(F43ZipCheck_ui)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        # Header
        self.header = QLabel("เลือกไฟล์ ZIP เพื่อทำการตรวจสอบแฟ้ม 43 ภายใน", F43ZipCheck_ui)
        try:
            self.header.setStyleSheet("font-size: 20px; font-weight: 700; color: #2c3e50;")
        except Exception:
            pass
        self.header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addWidget(self.header)

        # Zip file chooser group
        self.zip_group = QGroupBox("ไฟล์ ZIP")
        self.zip_group_layout = QFormLayout(self.zip_group)
        self.zip_group_layout.setContentsMargins(12, 12, 12, 12)
        self.zip_group_layout.setSpacing(8)

        self.zip_layout = QHBoxLayout()
        self.input_zip = QLineEdit(self.zip_group)
        self.input_zip.setPlaceholderText("เลือกไฟล์ .zip ที่มีแฟ้ม 43 แฟ้ม")
        self.btn_browse_zip = QPushButton("เลือกไฟล์ ZIP", self.zip_group)
        self.zip_layout.addWidget(self.input_zip)
        self.zip_layout.addWidget(self.btn_browse_zip)
        self.zip_group_layout.addRow("ที่อยู่ไฟล์:", self.zip_layout)
        self.main_layout.addWidget(self.zip_group)

        # Controls bar
        self.controls = QHBoxLayout()
        self.btn_scan = QPushButton("🔍 สแกนภายใน ZIP")
        self.btn_validate = QPushButton("✅ ตรวจสอบ")
        self.btn_export = QPushButton("💾 ส่งออกผลลัพธ์")
        self.controls.addWidget(self.btn_scan)
        self.controls.addWidget(self.btn_validate)
        self.controls.addWidget(self.btn_export)
        self.controls.addStretch(1)
        self.main_layout.addLayout(self.controls)

        # Splitter: results table and bottom log label
        self.splitter = QSplitter(F43ZipCheck_ui)
        self.splitter.setOrientation(Qt.Orientation.Vertical)

        self.table = QTableView(F43ZipCheck_ui)
        try:
            self.table.setStyleSheet(
                "QTableView::item:selected{background:#FFE5B4;color:black;}"
                "QTableView::item:selected:active{background:#FFE5B4;color:black;}"
                "QTableView::item:selected:!active{background:#FFE5B4;color:black;}"
            )
        except Exception:
            pass
        self.splitter.addWidget(self.table)

        self.log_label = QLabel("พร้อมทำงาน", F43ZipCheck_ui)
        try:
            self.log_label.setStyleSheet("font-family: Consolas, monospace; font-size: 13px;")
        except Exception:
            pass
        self.log_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.splitter.addWidget(self.log_label)

        try:
            self.splitter.setStretchFactor(0, 3)
            self.splitter.setStretchFactor(1, 1)
        except Exception:
            pass
        self.main_layout.addWidget(self.splitter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = F43ZipCheck_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
