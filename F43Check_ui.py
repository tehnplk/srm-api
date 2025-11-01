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
from PyQt6.QtGui import QFont, QStandardItemModel


class F43Check_ui(object):
    def setupUi(self, F43Check_ui):
        F43Check_ui.setWindowTitle("ตรวจสอบ43แฟ้ม")
        F43Check_ui.resize(1000, 700)

        self.main_layout = QVBoxLayout(F43Check_ui)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        # Header
        self.header = QLabel("ตรวจสอบมาตรฐานแฟ้ม 43 แฟ้ม", F43Check_ui)
        try:
            self.header.setStyleSheet("font-size: 20px; font-weight: 700; color: #2c3e50;")
        except Exception:
            pass
        self.header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addWidget(self.header)

        # Path chooser group
        self.path_group = QGroupBox("โฟลเดอร์แฟ้ม 43")
        self.path_group_layout = QFormLayout(self.path_group)
        self.path_group_layout.setContentsMargins(12, 12, 12, 12)
        self.path_group_layout.setSpacing(8)

        self.input_path_layout = QHBoxLayout()
        self.input_path = QLineEdit(self.path_group)
        self.input_path.setPlaceholderText("เลือกโฟลเดอร์ที่มีแฟ้ม 43 แฟ้ม")
        self.btn_browse = QPushButton("เลือกโฟลเดอร์", self.path_group)
        self.input_path_layout.addWidget(self.input_path)
        self.input_path_layout.addWidget(self.btn_browse)
        self.path_group_layout.addRow("ที่อยู่โฟลเดอร์:", self.input_path_layout)
        self.main_layout.addWidget(self.path_group)

        # Controls bar
        self.controls = QHBoxLayout()
        self.btn_scan = QPushButton("🔍 สแกนไฟล์")
        self.btn_validate = QPushButton("✅ ตรวจสอบ")
        self.btn_export = QPushButton("💾 ส่งออกผลลัพธ์")
        self.controls.addWidget(self.btn_scan)
        self.controls.addWidget(self.btn_validate)
        self.controls.addWidget(self.btn_export)
        self.controls.addStretch(1)
        self.main_layout.addLayout(self.controls)

        # Splitter: top table results and bottom log
        self.splitter = QSplitter(F43Check_ui)
        self.splitter.setOrientation(Qt.Orientation.Vertical)

        # Table of files/validations
        self.table = QTableView(F43Check_ui)
        try:
            self.table.setStyleSheet(
                "QTableView::item:selected{background:#FFE5B4;color:black;}"
                "QTableView::item:selected:active{background:#FFE5B4;color:black;}"
                "QTableView::item:selected:!active{background:#FFE5B4;color:black;}"
            )
        except Exception:
            pass
        self.splitter.addWidget(self.table)

        # Log label (simple placeholder; logic may swap to QTextEdit)
        self.log_label = QLabel("พร้อมทำงาน", F43Check_ui)
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
    ui = F43Check_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
