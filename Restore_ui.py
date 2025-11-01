from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QProgressBar,
    QTextEdit,
    QGroupBox,
)
from PyQt6.QtCore import Qt, QLocale


class Restore_ui(object):
    def setupUi(self, Form: QWidget):
        Form.setObjectName("RestoreForm")
        Form.setWindowTitle("🧩 Restore HIS")
        try:
            Form.setStyleSheet(
                """
                QWidget { background-color: #f5f7fb; }
                QGroupBox { background: #ffffff; border: 1px solid #e6e8ef; border-radius: 10px; margin-top: 12px; }
                QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
                QLineEdit { background: #ffffff; border: 1px solid #d9dee9; border-radius: 8px; padding: 8px 10px; }
                QPushButton { background-color: #0d6efd; color: #ffffff; border: 1px solid #0b5ed7; border-radius: 8px; padding: 8px 14px; font-weight: 600; }
                QPushButton:hover { background-color: #0b5ed7; }
                QPushButton:pressed { background-color: #0a58ca; }
                QPushButton:disabled { background-color: #cbd5e1; color: #6b7280; border-color: #cbd5e1; }
                QProgressBar { border: 1px solid #e6e8ef; border-radius: 8px; background: #ffffff; text-align: center; }
                QProgressBar::chunk { background-color: #22c55e; border-radius: 8px; }
                QTextEdit { background: #ffffff; border: 1px solid #e6e8ef; border-radius: 8px; }
                """
            )
        except Exception:
            pass

        root = QVBoxLayout(Form)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Source zip
        box_src = QGroupBox("ไฟล์สำรอง (ZIP)")
        ly_src = QHBoxLayout()
        self.txt_zip = QLineEdit()
        self.btn_browse = QPushButton("เลือกไฟล์…")
        ly_src.addWidget(self.txt_zip)
        ly_src.addWidget(self.btn_browse)
        box_src.setLayout(ly_src)
        root.addWidget(box_src)

        # Controls
        box_ctrl = QGroupBox("ควบคุม")
        ly_ctrl = QHBoxLayout()
        self.btn_start = QPushButton("เริ่ม Restore")
        self.btn_stop = QPushButton("หยุด")
        self.btn_stop.setEnabled(False)
        ly_ctrl.addWidget(self.btn_start)
        ly_ctrl.addWidget(self.btn_stop)
        box_ctrl.setLayout(ly_ctrl)
        root.addWidget(box_ctrl)

        # Overall progress
        box_p1 = QGroupBox("ความคืบหน้า (รวม)")
        ly_p1 = QVBoxLayout()
        self.progress_overall = QProgressBar()
        self.progress_overall.setRange(0, 100)
        self.progress_overall.setValue(0)
        try:
            self.progress_overall.setTextVisible(True)
            self.progress_overall.setFormat("%p%")
            self.progress_overall.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        except Exception:
            pass
        ly_p1.addWidget(self.progress_overall)
        box_p1.setLayout(ly_p1)
        root.addWidget(box_p1)

        # Per-file progress
        box_p2 = QGroupBox("ความคืบหน้า (ไฟล์ปัจจุบัน)")
        ly_p2 = QVBoxLayout()
        self.progress_file = QProgressBar()
        self.progress_file.setRange(0, 100)
        self.progress_file.setValue(0)
        try:
            self.progress_file.setTextVisible(True)
            self.progress_file.setFormat("%p%")
            self.progress_file.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        except Exception:
            pass
        ly_p2.addWidget(self.progress_file)
        box_p2.setLayout(ly_p2)
        root.addWidget(box_p2)

        # Log
        box_log = QGroupBox("บันทึกการทำงาน")
        ly_log = QVBoxLayout()
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        ly_log.addWidget(self.txt_log)
        box_log.setLayout(ly_log)
        root.addWidget(box_log)
