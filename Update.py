import sys
import os
import json
import shutil
import tempfile
import zipfile
import requests
from PyQt6.QtWidgets import (
    QWidget,
    QDialog,
    QMessageBox,
    QApplication,
)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl, QObject, pyqtSignal, QThread
from Version import CODE as CUR_CODE, NAME as CUR_NAME, RELEASE as CUR_RELEASE

from Update_ui import Update_ui


class Update(QDialog, Update_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.remote_download_url = ""
        self._thread: QThread | None = None
        self._worker: QObject | None = None
        # Initialize UI values from Version.py (no try/except; show errors in console if any)
        self.lbl_cur.setText(f"เวอร์ชัน: {CUR_NAME}  |  โค้ด: {CUR_CODE}  |  เผยแพร่: {CUR_RELEASE}")
        self.lbl_new.setText("ยังไม่ได้ตรวจสอบอัปเดต")
        self.lbl_notes.setText("")
        # This updater is download-only: disable/hide the check button
        try:
            self.btn_check.setEnabled(False)
            self.btn_check.setVisible(False)
        except Exception:
            pass
        # Wire download button
        self.btn_open.clicked.connect(self.start_download_and_install)
        self.btn_open.setEnabled(False)
        # Load new.txt to get URL and info
        self._load_new_file()

    

    def _parse_semver(self, v: str):
        try:
            parts = [int(p) for p in str(v or "").split('.')]
            return tuple(parts + [0] * (3 - len(parts)))[:3]
        except Exception:
            return (0, 0, 0)

    def _is_newer(self, remote_code: str | int | None, remote_name: str | None) -> bool:
        # Only consider numeric codes. If new code cannot be obtained, no update.
        try:
            rc = int(str(remote_code)) if remote_code is not None and str(remote_code).strip() != '' else None
        except Exception:
            rc = None
        try:
            lc = int(str(CUR_CODE)) if str(CUR_CODE).strip() != '' else None
        except Exception:
            lc = None
        if rc is None or lc is None:
            return False
        return rc > lc

    def _load_new_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        new_path = os.path.join(script_dir, 'new.txt')
        if not os.path.exists(new_path):
            self.lbl_status.setText("ไม่พบไฟล์ new.txt กรุณาตรวจสอบจากโปรแกรมหลัก")
            return
        with open(new_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        try:
            data = json.loads(raw)
        except Exception as e:
            self.lbl_status.setText(f"อ่าน new.txt ไม่ได้: {e}")
            return
        # Map keys from file (written by Main)
        r_name = str(data.get('new_version_name') or data.get('name') or '')
        r_code = data.get('new_version_code') if 'new_version_code' in data else data.get('code')
        r_release_raw = str(data.get('release') or '')
        r_release = r_release_raw[:10] if 'T' in r_release_raw and len(r_release_raw) >= 10 else r_release_raw
        r_url = str(
            data.get('download_url')
            or data.get('download')
            or data.get('url')
            or ''
        )
        r_notes = str(data.get('notes') or data.get('changelog') or '')

        # Populate UI
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
        if r_url:
            self.lbl_status.setText("พร้อมดาวน์โหลดและติดตั้ง")
        else:
            self.lbl_status.setText("ไม่พบลิงก์ดาวน์โหลดใน new.txt")

    def _cleanup_thread(self):
        self.btn_check.setEnabled(True)
        self._worker = None
        self._thread = None

    def _on_update_failed(self, message: str):
        print(f"[UPDATE] Failed: {message}")
        QMessageBox.warning(self, "อัปเดต", f"ตรวจสอบอัปเดตล้มเหลว: {message}")

    def _on_update_finished(self, data: dict):
        print(f"[UPDATE] Finished with data: {data}")
        # Map possible keys
        r_name = str(data.get('new_version_name') or data.get('name') or '')
        r_code = data.get('new_version_code') if 'new_version_code' in data else data.get('code')
        r_release_raw = str(data.get('release') or '')
        r_release = r_release_raw[:10] if 'T' in r_release_raw and len(r_release_raw) >= 10 else r_release_raw
        r_url = str(
            data.get('download_url')
            or data.get('download')
            or data.get('url')
            or ''
        )
        r_notes = str(data.get('notes') or data.get('changelog') or '')
        print(f"[UPDATE] Parsed remote -> name={r_name!r} code={r_code!r} release={r_release!r} url={r_url!r}")

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
        # Decide if newer
        is_newer = self._is_newer(r_code, r_name)
        # Enable download only when newer and URL is available
        can_download = bool(r_url) and is_newer
        self.btn_open.setEnabled(can_download)
        if not r_url:
            self.lbl_status.setText("ไม่พบลิงก์ดาวน์โหลด")
        elif not is_newer:
            self.lbl_status.setText("เป็นเวอร์ชันล่าสุดแล้ว ไม่จำเป็นต้องดาวน์โหลด")
        else:
            self.lbl_status.setText("พร้อมดาวน์โหลดและติดตั้ง")

        # Also show quick status dialog
        # is_newer already computed above
        print(f"[UPDATE] Compare -> current name={CUR_NAME!r} code={CUR_CODE!r} vs remote; newer={is_newer}")
        if is_newer:
            QMessageBox.information(self, "พบอัปเดต", "มีเวอร์ชันใหม่พร้อมใช้งาน")
        else:
            QMessageBox.information(self, "อัปเดต", "ขณะนี้เป็นเวอร์ชันล่าสุดแล้ว")

    def start_download_and_install(self):
        if not self.remote_download_url:
            QMessageBox.information(self, "อัปเดต", "ไม่พบลิงก์ดาวน์โหลด")
            return
        # Disable buttons during download
        self.btn_check.setEnabled(False)
        self.btn_open.setEnabled(False)
        self.progress.setValue(0)
        self.lbl_status.setText("กำลังดาวน์โหลด...")

        self._thread = QThread(self)
        self._worker = _DownloadWorker(self.remote_download_url)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_download_progress)
        self._worker.status.connect(self._on_download_status)
        self._worker.finished.connect(self._on_download_finished)
        self._worker.failed.connect(self._on_update_failed)
        # Cleanup wiring
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.start()

    def _on_download_progress(self, percent: int):
        if percent < 0:
            # indeterminate
            self.progress.setRange(0, 0)
        else:
            if self.progress.minimum() == 0 and self.progress.maximum() == 0:
                self.progress.setRange(0, 100)
            self.progress.setValue(max(0, min(100, percent)))

    def _on_download_status(self, message: str):
        self.lbl_status.setText(message)

    def _on_download_finished(self, message: str):
        self.lbl_status.setText(message)
        self.progress.setValue(100)
        QMessageBox.information(self, "อัปเดต", message)


class _UpdateWorker(QObject):
    # Retained for compatibility if needed in future; not used in download-only flow
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    def run(self):
        self.failed.emit("Update check is disabled in updater.")


class _DownloadWorker(QObject):
    progress = pyqtSignal(int)        # 0-100, or -1 for indeterminate
    status = pyqtSignal(str)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def _copy_tree(self, src: str, dst: str):
        for root, dirs, files in os.walk(src):
            rel = os.path.relpath(root, src)
            target_dir = os.path.join(dst, rel) if rel != '.' else dst
            os.makedirs(target_dir, exist_ok=True)
            for f in files:
                # Avoid overwriting the running updater itself
                if f.lower().startswith('update'):
                    continue
                src_file = os.path.join(root, f)
                dst_file = os.path.join(target_dir, f)
                shutil.copy2(src_file, dst_file)

    def run(self):
        try:
            self.status.emit("กำลังเชื่อมต่อเซิร์ฟเวอร์...")
            resp = requests.get(self.url, stream=True, timeout=30)
            if resp.status_code != 200:
                self.failed.emit(f"HTTP {resp.status_code}")
                return
            total = resp.headers.get('Content-Length') or resp.headers.get('content-length')
            total = int(total) if total is not None else None
            if total is None:
                self.progress.emit(-1)  # indeterminate
            else:
                self.progress.emit(0)

            fd, tmp_path = tempfile.mkstemp(suffix='.zip')
            os.close(fd)
            downloaded = 0
            with open(tmp_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024 * 64):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = int(downloaded * 100 / total)
                        self.progress.emit(pct)
            self.status.emit("ดาวน์โหลดเสร็จ กำลังแตกไฟล์...")

            extract_dir = tempfile.mkdtemp(prefix='hishelp_update_')
            with zipfile.ZipFile(tmp_path, 'r') as zf:
                zf.extractall(extract_dir)

            self.status.emit("กำลังติดตั้ง (แทนที่ไฟล์เก่า)...")
            app_dir = os.path.dirname(os.path.abspath(__file__))
            self._copy_tree(extract_dir, app_dir)

            try:
                os.remove(tmp_path)
            except Exception:
                pass
            try:
                shutil.rmtree(extract_dir, ignore_errors=True)
            except Exception:
                pass

            self.progress.emit(100)
            self.finished.emit("ติดตั้งเสร็จแล้ว กรุณาเปิดโปรแกรมใหม่")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.failed.emit(str(e))

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
