import sys
import traceback

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QTableView,
    QHBoxLayout,
    QPushButton,
    QApplication,
    QLineEdit,
    QFormLayout,
    QGroupBox,
    QTextEdit,
    QGridLayout,
    QTabWidget,
    QSplitter,
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt


class PersonalCheck_ui(object):
    def setupUi(self, PersonalCheck_ui):
        PersonalCheck_ui.setWindowTitle("Personal Check")
        PersonalCheck_ui.resize(900, 600)

        self.main_layout = QVBoxLayout(PersonalCheck_ui)
        self.main_layout.setContentsMargins(20, 8, 20, 20)
        self.main_layout.setSpacing(10)

        # Header label
        self.header_label = QLabel("กรุณากรอกเลขบัตรประชาชน หรือ เสียบบัตรประชาชนผู้รับบริการ", PersonalCheck_ui)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            self.header_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #2c3e50;")
        except Exception as e:
            traceback.print_exc()
        # Note: header will be placed inside input group box below

        # Create 13 separate input boxes for CID digits
        self.cid_layout = QHBoxLayout()
        self.cid_layout.setSpacing(6)
        self.cid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cid_edits = []
        for i in range(13):
            edit = QLineEdit(PersonalCheck_ui)
            edit.setObjectName(f"cid_edit_{i}")
            edit.setMaxLength(1)
            edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            edit.setFixedSize(48, 56)
            try:
                edit.setStyleSheet("font-size: 32px; background-color: #0d6efd; color: #ffffff;")
            except Exception as e:
                traceback.print_exc()
            self.cid_edits.append(edit)
            self.cid_layout.addWidget(edit)
            # Insert dash separators after positions 0, 4, 9, 11 (1-2345-67890-12-3)
            if i in (0, 4, 9, 11):
                dash = QLabel("-", PersonalCheck_ui)
                try:
                    dash.setStyleSheet("font-size: 28px; color: #666;")
                except Exception as e:
                    traceback.print_exc()
                dash.setFixedWidth(14)
                dash.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.cid_layout.addWidget(dash)
        # Build input group box
        self.group_input = QGroupBox("เลขบัตรประชาชน")
        self.group_input_layout = QVBoxLayout(self.group_input)
        self.group_input_layout.setContentsMargins(12, 12, 12, 12)
        self.group_input_layout.setSpacing(8)
        try:
            self.group_input.setStyleSheet(
                """
                QGroupBox { font-size: 16px; font-weight: 600; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
                """
            )
        except Exception as e:
            traceback.print_exc()
        self.group_input_layout.addWidget(self.header_label)
        self.group_input_layout.addLayout(self.cid_layout)
        self.main_layout.addWidget(self.group_input)

        # Leave focus/behaviors to logic layer

        # Result section labels (UI only; values to be set in logic)
        self.result_grid = QGridLayout()
        self.result_grid.setContentsMargins(10, 12, 10, 0)
        self.result_grid.setHorizontalSpacing(16)
        self.result_grid.setVerticalSpacing(8)

        # Basic info fields per API response
        self.value_check_date = QLabel("-", PersonalCheck_ui)
        self.value_pid = QLabel("-", PersonalCheck_ui)
        self.value_tname = QLabel("-", PersonalCheck_ui)
        self.value_fname = QLabel("-", PersonalCheck_ui)
        self.value_lname = QLabel("-", PersonalCheck_ui)
        self.value_nation = QLabel("-", PersonalCheck_ui)
        self.value_birth_date = QLabel("-", PersonalCheck_ui)
        self.value_sex = QLabel("-", PersonalCheck_ui)

        self.value_check_date.setObjectName("value_check_date")
        self.value_pid.setObjectName("value_pid")
        self.value_tname.setObjectName("value_tname")
        self.value_fname.setObjectName("value_fname")
        self.value_lname.setObjectName("value_lname")
        self.value_nation.setObjectName("value_nation")
        self.value_birth_date.setObjectName("value_birth_date")
        self.value_sex.setObjectName("value_sex")

        try:
            for w in [
                self.value_check_date,
                self.value_pid,
                self.value_tname,
                self.value_fname,
                self.value_lname,
                self.value_nation,
                self.value_birth_date,
                self.value_sex,
            ]:
                w.setStyleSheet("font-size: 18px; font-weight: 600;")
        except Exception as e:
            traceback.print_exc()

        def title(text):
            lbl = QLabel(text)
            try:
                lbl.setStyleSheet("color: #555; font-size: 14px;")
            except Exception as e:
                traceback.print_exc()
            return lbl

        # Row 0: วันที่ตรวจสอบ | เลขบัตรประชาชน
        self.result_grid.addWidget(title("วันที่ตรวจสอบ"), 0, 0)
        self.result_grid.addWidget(self.value_check_date, 0, 1)
        self.result_grid.addWidget(title("เลขบัตรประชาชน"), 0, 2)
        self.result_grid.addWidget(self.value_pid, 0, 3)

        # Row 1: คำนำหน้า | ชื่อ | นามสกุล
        self.result_grid.addWidget(title("คำนำหน้า"), 1, 0)
        self.result_grid.addWidget(self.value_tname, 1, 1)
        self.result_grid.addWidget(title("ชื่อ"), 1, 2)
        self.result_grid.addWidget(self.value_fname, 1, 3)
        self.result_grid.addWidget(title("นามสกุล"), 1, 4)
        self.result_grid.addWidget(self.value_lname, 1, 5)

        # Row 2: สัญชาติ | เพศ | วันเกิด
        self.result_grid.addWidget(title("สัญชาติ"), 2, 0)
        self.result_grid.addWidget(self.value_nation, 2, 1)
        self.result_grid.addWidget(title("เพศ"), 2, 2)
        self.result_grid.addWidget(self.value_sex, 2, 3)
        self.result_grid.addWidget(title("วันเกิด"), 2, 4)
        self.result_grid.addWidget(self.value_birth_date, 2, 5)

        self.value_main_inscl = QLabel("-", PersonalCheck_ui)
        self.value_sub_inscl = QLabel("-", PersonalCheck_ui)
        self.value_hosp_main = QLabel("-", PersonalCheck_ui)
        self.value_hosp_sub = QLabel("-", PersonalCheck_ui)
        self.value_right_no = QLabel("-", PersonalCheck_ui)

        self.value_main_inscl.setObjectName("value_main_inscl")
        self.value_sub_inscl.setObjectName("value_sub_inscl")
        self.value_hosp_main.setObjectName("value_hosp_main")
        self.value_hosp_sub.setObjectName("value_hosp_sub")
        self.value_right_no.setObjectName("value_right_no")

        # Style values for better readability
        try:
            self.value_main_inscl.setStyleSheet("font-size: 18px; font-weight: 600;")
            self.value_sub_inscl.setStyleSheet("font-size: 18px; font-weight: 600;")
            self.value_hosp_main.setStyleSheet("font-size: 18px; font-weight: 600;")
            self.value_hosp_sub.setStyleSheet("font-size: 18px; font-weight: 600;")
            self.value_right_no.setStyleSheet("font-size: 18px; font-weight: 600;")
        except Exception as e:
            traceback.print_exc()

        # Row 3: สิทธิหลัก | สิทธิย่อย
        self.result_grid.addWidget(title("สิทธิหลัก"), 3, 0)
        self.result_grid.addWidget(self.value_main_inscl, 3, 1, 1, 2)
        self.result_grid.addWidget(title("สิทธิย่อย"), 3, 3)
        self.result_grid.addWidget(self.value_sub_inscl, 3, 4, 1, 2)

        # Row 4: สถานบริการหลัก | สถานบริการรอง
        self.result_grid.addWidget(title("สถานบริการหลัก"), 4, 0)
        self.result_grid.addWidget(self.value_hosp_main, 4, 1, 1, 2)
        self.result_grid.addWidget(title("สถานบริการรอง"), 4, 3)
        self.result_grid.addWidget(self.value_hosp_sub, 4, 4, 1, 2)

        # Row 5: เลขที่สิทธิ (full width value)
        self.result_grid.addWidget(title("เลขที่สิทธิ"), 5, 0)
        self.result_grid.addWidget(self.value_right_no, 5, 1, 1, 5)

        # Row 6: Buttons at bottom right
        self.btn_refresh_token = QPushButton("🔄 Refresh Token", PersonalCheck_ui)
        try:
            self.btn_refresh_token.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: #ffffff;
                    border: 1px solid #17a2b8;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #138496; }
                QPushButton:pressed { background-color: #117a8b; }
                QPushButton:disabled { background-color: #6c757d; border-color: #6c757d; }
            """)
        except Exception as e:
            traceback.print_exc()
        self.btn_refresh_token.setMinimumWidth(120)
        # Add refresh token button to bottom right (column 4, row 6)
        self.result_grid.addWidget(self.btn_refresh_token, 6, 4, Qt.AlignmentFlag.AlignRight)
        
        self.btn_update_his = QPushButton("✅ อัพเดทสิทธิใน HIS", PersonalCheck_ui)
        try:
            self.btn_update_his.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: #ffffff;
                    border: 1px solid #28a745;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #218838; }
                QPushButton:pressed { background-color: #1e7e34; }
                QPushButton:disabled { background-color: #6c757d; border-color: #6c757d; }
            """)
        except Exception as e:
            traceback.print_exc()
        self.btn_update_his.setMinimumWidth(140)
        # Add button to bottom right (column 5, row 6)
        self.result_grid.addWidget(self.btn_update_his, 6, 5, Qt.AlignmentFlag.AlignRight)

        # Build result group box
        self.group_result = QGroupBox("ผลการตรวจสอบสิทธิ")
        self.group_result_layout = QVBoxLayout(self.group_result)
        self.group_result_layout.setContentsMargins(12, 12, 12, 12)
        self.group_result_layout.setSpacing(6)
        try:
            self.group_result.setStyleSheet(
                """
                QGroupBox { 
                    font-size: 16px; 
                    font-weight: 600; 
                    background-color: #ffffff; 
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; background-color: transparent; }
                """
            )
        except Exception as e:
            traceback.print_exc()
        self.group_result_layout.addLayout(self.result_grid)

        # Log tabs at the bottom
        self.log_tabs = QTabWidget(PersonalCheck_ui)
        self.log_tabs.setObjectName("log_tabs")
        try:
            self.log_tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #e0e0e0; }")
        except Exception as e:
            traceback.print_exc()

        # Tab 1: Log
        self.log_text = QTextEdit(PersonalCheck_ui)
        self.log_text.setReadOnly(True)
        try:
            self.log_text.setStyleSheet("font-family: Consolas, monospace; font-size: 13px;")
        except Exception as e:
            traceback.print_exc()
        self.log_tabs.addTab(self.log_text, "Log")

        # Tab 2: Response (raw)
        self.raw_text = QTextEdit(PersonalCheck_ui)
        self.raw_text.setReadOnly(True)
        try:
            self.raw_text.setStyleSheet("font-family: Consolas, monospace; font-size: 13px;")
        except Exception as e:
            traceback.print_exc()
        self.log_tabs.addTab(self.raw_text, "Response")

        # Splitter between result and logs (vertical)
        self.result_log_splitter = QSplitter(PersonalCheck_ui)
        self.result_log_splitter.setOrientation(Qt.Orientation.Vertical)
        self.result_log_splitter.addWidget(self.group_result)
        self.result_log_splitter.addWidget(self.log_tabs)
        try:
            # Give more space to result by default
            self.result_log_splitter.setStretchFactor(0, 3)
            self.result_log_splitter.setStretchFactor(1, 2)
        except Exception as e:
            traceback.print_exc()
        self.main_layout.addWidget(self.result_log_splitter)

    def retranslateUi(self, PersonalCheck_ui):
        PersonalCheck_ui.setWindowTitle("Personal Check")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = PersonalCheck_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
