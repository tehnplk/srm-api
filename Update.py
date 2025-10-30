import sys
import json
import urllib.request
from PyQt6.QtWidgets import (
    QWidget,
    QDialog,
    QMessageBox,
    QApplication,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtCore import QUrl, Qt
from Version import CODE as CUR_CODE, NAME as CUR_NAME, RELEASE as CUR_RELEASE

from Update_ui import Update_ui


class Update(QDialog, Update_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.remote_download_url = ""
        # Remove all widgets from the template UI and build our modern UI
        self._remove_all_widgets()
        self._build_ui()

    def _remove_all_widgets(self):
        def _clear_layout(layout):
            if layout is None:
                return
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.setParent(None)
                    w.deleteLater()
                else:
                    child_layout = item.layout()
                    if child_layout is not None:
                        _clear_layout(child_layout)
            layout.update()
        try:
            main_layout = getattr(self, 'main_layout', None)
            _clear_layout(main_layout)
        except Exception:
            pass

    def _build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("อัปเดตโปรแกรม HisHelp")
        tf = QFont()
        tf.setPointSize(16)
        tf.setBold(True)
        title.setFont(tf)
        layout.addWidget(title)

        # Current version block
        cur_title = QLabel("เวอร์ชันปัจจุบัน")
        cf = QFont()
        cf.setPointSize(12)
        cf.setBold(True)
        cur_title.setFont(cf)
        layout.addWidget(cur_title)

        self.lbl_cur = QLabel(f"เวอร์ชัน: {CUR_NAME}  |  โค้ด: {CUR_CODE}  |  เผยแพร่: {CUR_RELEASE}")
        self.lbl_cur.setWordWrap(True)
        layout.addWidget(self.lbl_cur)

        # Separator
        sep1 = QLabel("")
        sep1.setFixedHeight(6)
        layout.addWidget(sep1)

        # Remote version block
        new_title = QLabel("เวอร์ชันใหม่")
        new_title.setFont(cf)
        layout.addWidget(new_title)

        self.lbl_new = QLabel("ยังไม่ได้ตรวจสอบอัปเดต")
        self.lbl_new.setWordWrap(True)
        layout.addWidget(self.lbl_new)

        self.lbl_notes = QLabel("")
        self.lbl_notes.setWordWrap(True)
        self.lbl_notes.setStyleSheet("color: #444;")
        layout.addWidget(self.lbl_notes)

        # Buttons
        btn_row = QHBoxLayout()
        layout.addLayout(btn_row)
        btn_row.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.btn_check = QPushButton("🔄 ตรวจสอบอัปเดต")
        self.btn_open = QPushButton("⬇️ เปิดหน้าดาวน์โหลด")
        self.btn_open.setEnabled(False)
        btn_row.addWidget(self.btn_check)
        btn_row.addWidget(self.btn_open)

        # Connect
        try:
            self.btn_check.clicked.connect(self.check_update)
            self.btn_open.clicked.connect(self.open_download)
        except Exception:
            pass

        # Initial sizing
        self.setMinimumWidth(560)
        self.setMinimumHeight(320)
        self.setWindowTitle("ตรวจสอบอัปเดต HisHelp")

    def _parse_semver(self, v: str):
        try:
            parts = [int(p) for p in str(v or "").split('.')]
            return tuple(parts + [0] * (3 - len(parts)))[:3]
        except Exception:
            return (0, 0, 0)

    def _is_newer(self, remote_code: str | int | None, remote_name: str | None) -> bool:
        try:
            rc = int(str(remote_code)) if remote_code is not None and str(remote_code).strip() != '' else None
        except Exception:
            rc = None
        try:
            lc = int(str(CUR_CODE)) if str(CUR_CODE).strip() != '' else None
        except Exception:
            lc = None
        if rc is not None and lc is not None and rc != lc:
            return rc > lc
        rn = self._parse_semver(remote_name or "")
        ln = self._parse_semver(CUR_NAME or "")
        return rn > ln

    def check_update(self, url: str = "https://script.google.com/macros/s/AKfycbxD9CI91jGbL-MWHvBDvCqgh8s9DaTEZ38ItvX7yX37w65mQzWC_DQ5SzlrViEooh9wtg/exec"):
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                if resp.status != 200:
                    QMessageBox.warning(self, "อัปเดต", f"ตรวจสอบอัปเดตล้มเหลว: HTTP {resp.status}")
                    return
                raw = resp.read().decode('utf-8')
                payload = json.loads(raw)
        except Exception as e:
            QMessageBox.warning(self, "อัปเดต", f"ตรวจสอบอัปเดตล้มเหลว: {e}")
            return

        # Normalize to dict (API may return a list with a single object)
        if isinstance(payload, list):
            data = payload[0] if payload else {}
        else:
            data = payload if isinstance(payload, dict) else {}

        # Map possible keys
        r_name = str(data.get('new_version_name') or data.get('name') or '')
        r_code = data.get('new_version_code') if 'new_version_code' in data else data.get('code')
        r_release_raw = str(data.get('release') or '')
        # Try to format ISO datetime (e.g., 2025-10-29T17:00:00.000Z) to YYYY-MM-DD
        r_release = r_release_raw[:10] if 'T' in r_release_raw and len(r_release_raw) >= 10 else r_release_raw
        r_url = str(data.get('download') or data.get('url') or '')
        r_notes = str(data.get('notes') or data.get('changelog') or '')

        # Update UI with remote info
        new_info = []
        if r_name:
            new_info.append(f"เวอร์ชัน: {r_name}")
        if r_code is not None and str(r_code) != '':
            new_info.append(f"โค้ด: {r_code}")
        if r_release:
            new_info.append(f"เผยแพร่: {r_release}")
        self.lbl_new.setText("  |  ".join(new_info) if new_info else "ไม่พบข้อมูลเวอร์ชันใหม่")
        self.lbl_notes.setText(r_notes)
        self.remote_download_url = r_url
        self.btn_open.setEnabled(bool(r_url))

        # Also show quick status dialog
        if self._is_newer(r_code, r_name):
            QMessageBox.information(self, "พบอัปเดต", "มีเวอร์ชันใหม่พร้อมใช้งาน")
        else:
            QMessageBox.information(self, "อัปเดต", "ขณะนี้เป็นเวอร์ชันล่าสุดแล้ว")

    def open_download(self):
        if not self.remote_download_url:
            return
        try:
            QDesktopServices.openUrl(QUrl(self.remote_download_url))
        except Exception:
            pass

    def add_item(self):
        """
        Handle Add button click.
        """
        QMessageBox.information(self, "Add", "Add functionality will be implemented here.")

    def edit_item(self):
        """
        Handle Edit button click.
        """
        QMessageBox.information(self, "Edit", "Edit functionality will be implemented here.")

    def delete_item(self):
        """
        Handle Delete button click.
        """
        reply = QMessageBox.question(
            self,
            "Delete",
            "Are you sure you want to delete the selected item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        # Placeholder: handle reply if needed

    def refresh_data(self):
        """
        Handle Refresh button click.
        """
        QMessageBox.information(self, "Refresh", "Data refreshed successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Update()
    window.show()
    sys.exit(app.exec())
