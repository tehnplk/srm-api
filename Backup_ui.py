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


class Backup_ui(object):
    def setupUi(self, Form: QWidget):
        Form.setObjectName("BackupForm")
        Form.setWindowTitle("🗄️ Backup HIS")
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

        # Destination
        box_dest = QGroupBox("ปลายทางไฟล์ ZIP")
        ly_dest = QHBoxLayout()
        self.txt_dest = QLineEdit()
        self.txt_dest.setPlaceholderText("เลือกโฟลเดอร์ปลายทางสำหรับไฟล์ zip")
        self.btn_browse = QPushButton("เลือกโฟลเดอร์…")
        ly_dest.addWidget(self.txt_dest, 1)
        ly_dest.addWidget(self.btn_browse, 0)
        box_dest.setLayout(ly_dest)
        root.addWidget(box_dest)

        # Controls
        box_ctrl = QGroupBox("การทำงาน")
        ly_ctrl = QHBoxLayout()
        self.btn_start = QPushButton("เริ่ม Backup")
        self.btn_stop = QPushButton("หยุด")
        self.btn_stop.setEnabled(False)
        ly_ctrl.addWidget(self.btn_start)
        ly_ctrl.addWidget(self.btn_stop)
        box_ctrl.setLayout(ly_ctrl)
        root.addWidget(box_ctrl)

        # Progress
        box_prog = QGroupBox("ความคืบหน้า")
        ly_prog = QVBoxLayout()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        try:
            self.progress.setTextVisible(True)
            self.progress.setFormat("%p%")
            try:
                self.progress.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
            except Exception:
                pass
        except Exception:
            pass
        ly_prog.addWidget(self.progress)
        box_prog.setLayout(ly_prog)
        root.addWidget(box_prog)

        # Log
        box_log = QGroupBox("บันทึกการทำงาน")
        ly_log = QVBoxLayout()
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        ly_log.addWidget(self.txt_log)
        box_log.setLayout(ly_log)
        root.addWidget(box_log, 1)

        # Wire browse dialog (logic in Backup class will connect slots)
        # Buttons are exposed as attributes
