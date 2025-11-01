import os
import re
import zipfile
import tempfile
import shutil
import traceback

from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt6.QtCore import QSettings, QThread, pyqtSignal, QObject

from Restore_ui import Restore_ui


class Restore(QWidget, Restore_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings = QSettings("SRM_API", "MySQL_Settings")
        self.btn_browse.clicked.connect(self.on_browse)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        try:
            last = str(self.settings.value("restore_last_zip", "") or "")
            if last and os.path.isfile(last):
                self.txt_zip.setText(last)
        except Exception:
            print("restore init error:")
            traceback.print_exc()
        self._thread = None
        self._worker = None

    def _get_db_config(self):
        return {
            "host": self.settings.value("host", "localhost"),
            "port": int(self.settings.value("port", 3306)),
            "user": self.settings.value("user", ""),
            "password": self.settings.value("password", ""),
            "database": self.settings.value("database", ""),
            "charset": "utf8mb4",
            "connect_timeout": int(self.settings.value("timeout", 10)),
        }

    def _ensure_config_complete(self) -> bool:
        cfg = self._get_db_config()
        missing = [k for k in ("host", "user", "database") if not str(cfg.get(k, "")).strip()]
        if missing:
            QMessageBox.warning(self, "การตั้งค่าไม่ครบ", f"โปรดตั้งค่า: {', '.join(missing)} ในเมนู ตั้งค่า")
            return False
        return True

    def on_browse(self):
        try:
            last_dir = os.path.dirname(self.txt_zip.text().strip()) if self.txt_zip.text().strip() else os.path.expanduser("~")
            file_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ ZIP สำรอง", last_dir, "Zip Files (*.zip)")
            if file_path:
                self.txt_zip.setText(file_path)
                try:
                    self.settings.setValue("restore_last_zip", file_path)
                    self.settings.sync()
                except Exception:
                    print("store last zip error:")
                    traceback.print_exc()
        except Exception:
            traceback.print_exc()

    def on_start(self):
        if not self._ensure_config_complete():
            return
        zip_path = (self.txt_zip.text() or "").strip()
        if not zip_path or not os.path.isfile(zip_path):
            QMessageBox.warning(self, "ไม่พบไฟล์", "โปรดเลือกไฟล์ .zip สำรอง")
            return
        try:
            self.btn_start.setEnabled(False)
            self.btn_browse.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.txt_log.clear()
            self.progress_overall.setValue(0)
            self.progress_file.setValue(0)
            cfg = self._get_db_config()
            self._thread = QThread(self)
            self._worker = RestoreWorker(cfg, zip_path)
            self._worker.moveToThread(self._thread)
            self._thread.started.connect(self._worker.run)
            self._worker.log_line.connect(self.on_log)
            self._worker.progress_overall.connect(self.progress_overall.setValue)
            self._worker.progress_file.connect(self.progress_file.setValue)
            self._worker.finished_ok.connect(self.on_finished_ok)
            self._worker.finished_error.connect(self.on_finished_error)
            self._worker.ask_ui_reset.connect(self.on_ui_reset)
            self._thread.start()
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "ผิดพลาด", "เริ่ม Restore ไม่สำเร็จ")

    def on_stop(self):
        try:
            if self._worker:
                self._worker.request_stop()
        except Exception:
            traceback.print_exc()

    def on_ui_reset(self):
        try:
            self.btn_start.setEnabled(True)
            self.btn_browse.setEnabled(True)
            self.btn_stop.setEnabled(False)
        except Exception:
            traceback.print_exc()

    def on_log(self, text: str):
        try:
            self.txt_log.append(text)
        except Exception:
            traceback.print_exc()

    def on_finished_ok(self, msg: str):
        try:
            self.on_ui_reset()
            QMessageBox.information(self, "สำเร็จ", msg)
        except Exception:
            traceback.print_exc()

    def on_finished_error(self, err: str):
        try:
            self.on_ui_reset()
            QMessageBox.critical(self, "ผิดพลาด", err)
        except Exception:
            traceback.print_exc()


class RestoreWorker(QObject):
    log_line = pyqtSignal(str)
    progress_overall = pyqtSignal(int)
    progress_file = pyqtSignal(int)
    finished_ok = pyqtSignal(str)
    finished_error = pyqtSignal(str)
    ask_ui_reset = pyqtSignal()

    def __init__(self, db_config: dict, zip_path: str):
        super().__init__()
        self._db_config = db_config
        self._zip_path = zip_path
        self._stop = False

    def request_stop(self):
        self._stop = True

    def _exec_sql_file(self, conn, file_path: str):
        import pymysql
        from pymysql.constants import CLIENT
        self.progress_file.emit(0)
        total_lines = 0
        try:
            with open(file_path, 'rb') as f:
                total_lines = sum(1 for _ in f)
        except Exception:
            traceback.print_exc()
        executed = 0
        delimiter = b';'
        buf = b''
        with open(file_path, 'rb') as f:
            for line in f:
                if self._stop:
                    return False
                ls = line.strip()
                if ls.upper().startswith(b'DELIMITER '):
                    try:
                        delimiter = ls.split(maxsplit=1)[1]
                    except Exception:
                        delimiter = b';'
                    continue
                buf += line
                if buf.rstrip().endswith(delimiter + b"\n") or buf.rstrip().endswith(delimiter + b"\r\n") or buf.rstrip().endswith(delimiter):
                    try:
                        with conn.cursor(pymysql.cursors.SSCursor) as cursor:
                            cursor.execute(buf)
                            conn.commit()
                    except Exception as e:
                        print("exec error:", e)
                        self.log_line.emit(f"ERROR: {os.path.basename(file_path)} -> {e}")
                    buf = b''
                executed += 1
                if total_lines:
                    p = int(executed * 100 / total_lines)
                    self.progress_file.emit(min(100, max(0, p)))
        return True

    def run(self):
        import pymysql
        import uuid
        tmp_dir = None
        try:
            self.log_line.emit("กำลังเชื่อมต่อฐานข้อมูล…")
            conn = pymysql.connect(
                host=self._db_config.get('host'),
                port=int(self._db_config.get('port') or 3306),
                user=self._db_config.get('user'),
                password=self._db_config.get('password'),
                database=self._db_config.get('database'),
                charset=self._db_config.get('charset') or 'tis620',
                client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
            )
            try:
                with conn.cursor() as _cur:
                    _cur.execute("SET NAMES tis620;")
                    _cur.execute("SET CHARACTER SET tis620;")
                    _cur.execute("SET collation_connection = 'tis620_general_ci';")
                    _cur.execute("SET sql_mode='';")
                    _cur.execute("SET innodb_strict_mode=0;")
            except Exception:
                traceback.print_exc()
            tmp_dir = tempfile.mkdtemp(prefix="restore_")
            self.log_line.emit("กำลังแตกไฟล์ ZIP…")
            with zipfile.ZipFile(self._zip_path, 'r') as zf:
                zf.extractall(tmp_dir)
            files = [f for f in os.listdir(tmp_dir) if os.path.isfile(os.path.join(tmp_dir, f)) and f.lower().endswith('.sql')]
            files.sort()
            total = max(1, len(files))
            done = 0
            for fname in files:
                if self._stop:
                    self.log_line.emit("หยุดโดยผู้ใช้")
                    self.ask_ui_reset.emit()
                    return
                p = int(done * 100 / total)
                self.progress_overall.emit(p)
                fpath = os.path.join(tmp_dir, fname)
                self.log_line.emit(f"กำลังนำเข้าไฟล์: {fname}")
                ok = self._exec_sql_file(conn, fpath)
                done += 1
                self.progress_overall.emit(int(done * 100 / total))
                if not ok:
                    break
            self.progress_file.emit(100)
            self.progress_overall.emit(100)
            self.finished_ok.emit("นำเข้าข้อมูลเสร็จสิ้น")
        except Exception as e:
            print("restore run error:", e)
            traceback.print_exc()
            self.finished_error.emit(str(e))
        finally:
            try:
                if tmp_dir and os.path.isdir(tmp_dir):
                    shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                traceback.print_exc()
