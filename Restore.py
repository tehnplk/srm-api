import os
import re
import zipfile
import tempfile
import shutil
import traceback

from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt6.QtCore import QSettings, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QCloseEvent

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
            "charset": "tis620",
            "use_unicode": False,
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
            self.on_ui_reset()

    def on_stop(self):
        try:
            if self._worker:
                self._worker.request_stop()
        except Exception:
            traceback.print_exc()

    def _cleanup_thread(self):
        try:
            # Request stop first
            if self._worker:
                self._worker.request_stop()
            
            # Wait for thread to finish with timeout
            if self._thread:
                if self._thread.isRunning():
                    self._thread.quit()
                    if not self._thread.wait(3000):  # 3 second timeout
                        # Force terminate if still running
                        try:
                            self._thread.terminate()
                            self._thread.wait(1000)  # Additional 1 second for termination
                        except Exception:
                            pass
        except Exception:
            traceback.print_exc()
        self._thread = None
        self._worker = None

    def closeEvent(self, event: QCloseEvent):
        """Handle form close event to clean up threads properly"""
        try:
            self.on_stop()  # Request stop
            self._cleanup_thread()  # Clean up thread
            event.accept()
        except Exception:
            traceback.print_exc()
            event.accept()  # Always accept close to prevent hanging

    def on_ui_reset(self):
        try:
            self.btn_start.setEnabled(True)
            self.btn_browse.setEnabled(True)
            self.btn_stop.setEnabled(False)
        except Exception:
            traceback.print_exc()
        self._cleanup_thread()

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
        self._conn = None  # Store connection for cleanup

    def request_stop(self):
        self._stop = True
        # Close connection to speed up stop
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _exec_sql_file(self, conn, file_path: str):
        import pymysql
        from pymysql.constants import CLIENT
        self.progress_file.emit(0)
        total_lines = 0
        try:
            with open(file_path, 'rb') as f:
                total_lines = sum(1 for _ in f)
        except Exception as e:
            print("count lines error:", e)
            self.log_line.emit(f"WARNING: Cannot count lines in {os.path.basename(file_path)}: {e}")
        executed = 0
        delimiter = b';'
        buf = b''
        error_count = 0
        navicat_tolerant_count = 0
        success_count = 0
        
        with open(file_path, 'rb') as f:
            for line in f:
                if self._stop:
                    self.ask_ui_reset.emit()
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
                        # Check if connection is still valid before executing
                        if not self._stop and conn and not getattr(conn, '_closed', False):
                            with conn.cursor(pymysql.cursors.SSCursor) as cursor:
                                cursor.execute(buf)
                                conn.commit()
                                success_count += 1
                        else:
                            self.ask_ui_reset.emit()
                            return False
                    except Exception as e:
                        if not self._stop:  # Only log errors if not intentionally stopped
                            print("exec error:", e)
                            
                            # Check if this is a Navicat-tolerant error
                            error_str = str(e).lower()
                            navicat_tolerant = any(err in error_str for err in [
                                'data too long for column',
                                'incorrect integer value',
                                'duplicate entry',
                                'truncated'
                            ])
                            
                            if navicat_tolerant:
                                navicat_tolerant_count += 1
                                # Log Navicat-tolerant errors as warnings (only first few)
                                if navicat_tolerant_count <= 5:
                                    self.log_line.emit(f"WARNING: {os.path.basename(file_path)} -> {e} (Navicat-tolerant)")
                            else:
                                error_count += 1
                                # Only log first 10 non-tolerant errors to avoid spam
                                if error_count <= 10:
                                    self.log_line.emit(f"ERROR: {os.path.basename(file_path)} -> {e}")
                                    # Show the problematic SQL for debugging
                                    if error_count <= 3:
                                        sql_preview = buf.decode('utf-8', 'ignore')[:200]
                                        self.log_line.emit(f"SQL Preview: {sql_preview}...")
                                elif error_count == 11:
                                    self.log_line.emit(f"ERROR: Too many errors in {os.path.basename(file_path)}, suppressing further messages")
                        else:
                            self.ask_ui_reset.emit()
                            return False
                    buf = b''
                executed += 1
                if total_lines:
                    p = int(executed * 100 / total_lines)
                    self.progress_file.emit(min(100, max(0, p)))
        
        # Log execution summary
        if not self._stop:
            if success_count > 0:
                self.log_line.emit(f"SUCCESS: {os.path.basename(file_path)} - {success_count} statements executed")
            if navicat_tolerant_count > 0:
                self.log_line.emit(f"INFO: {os.path.basename(file_path)} - {navicat_tolerant_count} Navicat-tolerant warnings (ignored)")
            if error_count > 0:
                self.log_line.emit(f"WARNING: {os.path.basename(file_path)} had {error_count} error(s)")
        
        return not self._stop  # Return True only if not stopped

    def run(self):
        import pymysql
        from pymysql.constants import FIELD_TYPE
        from pymysql import converters as pymysql_converters
        import uuid
        tmp_dir = None
        try:
            self.log_line.emit("กำลังเชื่อมต่อฐานข้อมูล…")
            
            # Use same connection configuration as Backup
            conv = pymysql_converters.conversions.copy()
            try:
                conv[FIELD_TYPE.DECIMAL] = lambda x: x
                conv[FIELD_TYPE.NEWDECIMAL] = lambda x: x
            except Exception:
                pass
            
            self._conn = pymysql.connect(**self._db_config, conv=conv)
            conn = self._conn
            
            # Apply Navicat-compatible SQL settings
            try:
                with conn.cursor() as _cur:
                    _cur.execute("SET NAMES tis620;")
                    _cur.execute("SET CHARACTER SET tis620;")
                    _cur.execute("SET collation_connection = 'tis620_general_ci';")
                    # Navicat uses very permissive SQL mode
                    _cur.execute("SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO,ALLOW_INVALID_DATES';")
                    _cur.execute("SET innodb_strict_mode=0;")
                    _cur.execute("SET FOREIGN_KEY_CHECKS=0;")
                    # Additional permissive settings for Navicat compatibility
                    _cur.execute("SET sql_mode = '';")
                    _cur.execute("SET @@session.sql_mode = 'NO_AUTO_VALUE_ON_ZERO';")
                    conn.commit()
            except Exception:
                traceback.print_exc()
                
            # Check if stop was requested during connection
            if self._stop:
                self.log_line.emit("หยุดโดยผู้ใช้")
                self.ask_ui_reset.emit()
                return
            tmp_dir = tempfile.mkdtemp(prefix="restore_")
            self.log_line.emit("กำลังแตกไฟล์ ZIP…")
            with zipfile.ZipFile(self._zip_path, 'r') as zf:
                zf.extractall(tmp_dir)
            files = [f for f in os.listdir(tmp_dir) if os.path.isfile(os.path.join(tmp_dir, f)) and f.lower().endswith('.sql')]
            files.sort()
            
            # Check if this is Navicat-style backup
            is_navicat_style = False
            if files:
                first_file = os.path.join(tmp_dir, files[0])
                try:
                    with open(first_file, 'r', encoding='utf-8') as f:
                        first_lines = ''.join(f.readlines(10))
                        if 'Navicat MySQL Data Transfer' in first_lines:
                            is_navicat_style = True
                            self.log_line.emit("ตรวจพบ Navicat-style backup")
                except Exception:
                    pass
            
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
                    # Break if stopped or error occurred
                    if self._stop:
                        return
                    break
            self.progress_file.emit(100)
            self.progress_overall.emit(100)
            
            # Re-enable foreign key checks at the end
            try:
                with conn.cursor() as _cur:
                    _cur.execute("SET FOREIGN_KEY_CHECKS=1;")
                    conn.commit()
            except Exception:
                traceback.print_exc()
            
            # Log completion summary
            if is_navicat_style:
                self.log_line.emit("Navicat-style restore completed successfully")
            else:
                self.log_line.emit("Restore completed successfully")
                
            self.finished_ok.emit("นำเข้าข้อมูลเสร็จสิ้น")
        except Exception as e:
            print("restore run error:", e)
            traceback.print_exc()
            self.finished_error.emit(str(e))
        finally:
            try:
                # Clean up connection
                if self._conn:
                    try:
                        self._conn.close()
                    except Exception:
                        pass
                    self._conn = None
                    
                # Clean up temp directory
                if tmp_dir and os.path.isdir(tmp_dir):
                    shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                traceback.print_exc()
