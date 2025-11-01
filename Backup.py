import os
import re
import traceback
import tempfile
import shutil
import zipfile
from datetime import datetime

from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt6.QtCore import QSettings, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QCloseEvent

from Backup_ui import Backup_ui
from pymysql.constants import FIELD_TYPE
from pymysql import converters as pymysql_converters


class Backup(QWidget, Backup_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings = QSettings("SRM_API", "MySQL_Settings")
        self.btn_browse.clicked.connect(self.on_browse)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        try:
            default_dir = os.path.join(os.path.expanduser("~"), "Documents")
            if not os.path.isdir(default_dir):
                default_dir = os.path.expanduser("~")
            last = str(self.settings.value("backup_dest", "") or "").strip()
            if last and os.path.isdir(last):
                self.txt_dest.setText(last)
            else:
                self.txt_dest.setText(default_dir)
        except Exception:
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
            d = QFileDialog.getExistingDirectory(self, "เลือกปลายทาง ZIP", self.txt_dest.text().strip() or os.path.expanduser("~"))
            if d:
                self.txt_dest.setText(d)
                try:
                    self.settings.setValue("backup_dest", d)
                    self.settings.sync()
                except Exception:
                    traceback.print_exc()
        except Exception:
            traceback.print_exc()

    def on_start(self):
        if not self._ensure_config_complete():
            return
        dest_dir = (self.txt_dest.text() or "").strip()
        if not dest_dir:
            QMessageBox.warning(self, "ปลายทางว่าง", "โปรดเลือกโฟลเดอร์ปลายทาง")
            return
        if not os.path.isdir(dest_dir):
            QMessageBox.warning(self, "ไม่พบโฟลเดอร์", "ปลายทางไม่ใช่โฟลเดอร์ที่มีอยู่")
            return
        try:
            try:
                self.settings.setValue("backup_dest", dest_dir)
                self.settings.sync()
            except Exception:
                traceback.print_exc()
            self.btn_start.setEnabled(False)
            self.btn_browse.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.txt_log.clear()
            self.progress.setValue(0)
            cfg = self._get_db_config()
            his_name = str(self.settings.value("system", "his") or "his")
            try:
                his_name = re.sub(r"[^A-Za-z0-9_-]+", "", his_name)
            except Exception:
                his_name = "his"
            stamp = datetime.now().strftime("%Y%m%d%H%M%S")
            zip_name = f"backup_{his_name}_{stamp}.zip"
            zip_path = os.path.join(dest_dir, zip_name)
            self._thread = QThread(self)
            self._worker = BackupWorker(cfg, zip_path)
            self._worker.moveToThread(self._thread)
            self._thread.started.connect(self._worker.run)
            self._worker.progress_changed.connect(self.on_progress)
            self._worker.log_line.connect(self.on_log)
            self._worker.finished_ok.connect(self.on_finished_ok)
            self._worker.finished_error.connect(self.on_finished_error)
            self._worker.ask_ui_reset.connect(self.on_ui_reset)
            self._thread.start()
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "ผิดพลาด", "เริ่มงานไม่สำเร็จ")
            self.on_ui_reset()

    def on_stop(self):
        try:
            if self._worker:
                self._worker.request_stop()
        except Exception:
            traceback.print_exc()

    def on_progress(self, pct: int):
        try:
            self.progress.setValue(max(0, min(100, int(pct))))
        except Exception:
            traceback.print_exc()

    def on_log(self, text: str):
        try:
            self.txt_log.append(text)
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

    def on_finished_ok(self, zip_path: str):
        try:
            self.on_log(f"เสร็จสิ้น: {zip_path}")
            QMessageBox.information(self, "สำเร็จ", f"บันทึกไฟล์แล้ว\n{zip_path}")
        except Exception:
            traceback.print_exc()
        self.on_ui_reset()

    def on_finished_error(self, err: str):
        try:
            self.on_log(f"ผิดพลาด: {err}")
            QMessageBox.critical(self, "ผิดพลาด", err)
        except Exception:
            traceback.print_exc()
        self.on_ui_reset()


class BackupWorker(QObject):
    progress_changed = pyqtSignal(int)
    log_line = pyqtSignal(str)
    finished_ok = pyqtSignal(str)
    finished_error = pyqtSignal(str)
    ask_ui_reset = pyqtSignal()

    def __init__(self, db_config: dict, zip_path: str):
        super().__init__()
        self._db_config = dict(db_config or {})
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

    def _escape(self, val, max_length=None):
        if val is None:
            return "''"  # Navicat uses empty string for null
        if isinstance(val, (int, float)):
            return f"'{val}'"  # Navicat quotes all numbers
        if isinstance(val, (bytes, bytearray)):
            try:
                return "0x" + bytes(val).hex()
            except Exception:
                return "''"
        try:
            s = str(val)
        except Exception:
            s = repr(val)
        
        # Handle string 'None' values - convert to empty string
        if s == 'None':
            s = ''
        
        # Handle data too long by truncating if max_length is specified
        if max_length and len(s) > max_length:
            s = s[:max_length]
            
        s = s.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{s}'"

    def run(self):
        import pymysql
        tmp_dir = None
        try:
            conv = pymysql_converters.conversions.copy()
            try:
                conv[FIELD_TYPE.DECIMAL] = lambda x: x
                conv[FIELD_TYPE.NEWDECIMAL] = lambda x: x
            except Exception:
                pass
            self._conn = pymysql.connect(**self._db_config, conv=conv)
            conn = self._conn
            
            # Check if stop was requested during connection
            if self._stop:
                self.log_line.emit("หยุดโดยผู้ใช้")
                self.ask_ui_reset.emit()
                return
            dbname = self._db_config.get("database")
            # Prepare header info from settings and server
            source_host = str(self._db_config.get("host") or "localhost")
            try:
                source_port = int(self._db_config.get("port") or 3306)
            except Exception:
                source_port = 3306
            source_server = f"{source_host}_{source_port}"
            source_host_line = f"{source_host}:{source_port}"
            source_version = "(unknown)"
            try:
                with conn.cursor() as cur_ver:
                    cur_ver.execute("SELECT VERSION()")
                    vrow = cur_ver.fetchone()
                    if vrow:
                        vv = vrow[0]
                        if isinstance(vv, (bytes, bytearray)):
                            try:
                                source_version = bytes(vv).decode('utf-8', 'ignore')
                            except Exception:
                                source_version = str(vv)
                        else:
                            source_version = str(vv)
            except Exception:
                traceback.print_exc()
            with conn.cursor() as cur:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE' ORDER BY table_name", (dbname,))
                def _as_text(x):
                    if isinstance(x, (bytes, bytearray)):
                        try:
                            return x.decode('utf-8', 'ignore')
                        except Exception:
                            return str(x)
                    return str(x)
                tables = [_as_text(r[0]) for r in (cur.fetchall() or [])]
                # Views
                try:
                    cur.execute("SELECT table_name FROM information_schema.views WHERE table_schema=%s ORDER BY table_name", (dbname,))
                    views = [_as_text(r[0]) for r in (cur.fetchall() or [])]
                except Exception:
                    traceback.print_exc()
                    views = []
                # Routines (PROCEDURE and FUNCTION)
                try:
                    cur.execute("SELECT ROUTINE_NAME, ROUTINE_TYPE FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=%s ORDER BY ROUTINE_NAME", (dbname,))
                    routines = [( _as_text(r[0]), _as_text(r[1]) ) for r in (cur.fetchall() or [])]
                except Exception:
                    traceback.print_exc()
                    routines = []
            total_items = max(1, len(tables) + len(views) + len(routines))
            tmp_dir = tempfile.mkdtemp(prefix="hisbak_")
            done = 0
            total_tables = len(tables)
            for t in tables:
                if self._stop:
                    self.log_line.emit("หยุดโดยผู้ใช้")
                    self.ask_ui_reset.emit()
                    return
                try:
                    self.log_line.emit(f"[{done+1}/{total_items}] กำลังสำรองตาราง: {t}")
                except Exception:
                    pass
                table_file = os.path.join(tmp_dir, f"{t}.sql")
                with open(table_file, "w", encoding="utf-8") as f:
                    # Header (Navicat-like)
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write("/*\n")
                    f.write("Navicat MySQL Data Transfer\n\n")
                    f.write(f"Source Server         : {source_server}\n")
                    f.write(f"Source Server Version : {source_version}\n")
                    f.write(f"Source Host           : {source_host_line}\n")
                    f.write(f"Source Database       : {self._db_config.get('database') or ''}\n\n")
                    f.write("Target Server Type    : MYSQL\n")
                    f.write(f"Target Server Version : {source_version}\n")
                    f.write("File Encoding         : 65001\n\n")
                    f.write(f"Date: {now_str}\n")
                    f.write("*/\n\n")
                    f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                    with conn.cursor() as cur:
                        cur.execute(f"SHOW CREATE TABLE `{t}`")
                        row = cur.fetchone()
                        create_sql = row[1] if row and len(row) > 1 else None
                        if isinstance(create_sql, (bytes, bytearray)):
                            try:
                                create_sql = create_sql.decode('utf-8', 'ignore')
                            except Exception:
                                create_sql = None
                        if create_sql:
                            f.write("-- ----------------------------\n")
                            f.write(f"-- Table structure for {t}\n")
                            f.write("-- ----------------------------\n")
                            f.write(f"DROP TABLE IF EXISTS `{t}`;\n")
                            f.write(create_sql + ";\n\n")
                        # Read all columns as raw bytes to avoid type conversions (e.g., DECIMAL)
                        cur.execute(f"SHOW COLUMNS FROM `{t}`")
                        col_rows = cur.fetchall() or []
                        col_names = []
                        col_is_numeric = []
                        col_is_datetime = []
                        col_is_stringy = []  # char/varchar/text/enum/set
                        col_is_blob = []     # blob/binary
                        col_max_lengths = []  # Store max lengths for string columns
                        for r in col_rows:
                            try:
                                name = r[0]
                                ctype = r[1] if len(r) > 1 else ''
                                if isinstance(name, (bytes, bytearray)):
                                    name = name.decode('utf-8', 'ignore')
                                else:
                                    name = str(name)
                                tstr = ''
                                if isinstance(ctype, (bytes, bytearray)):
                                    try:
                                        tstr = ctype.decode('utf-8', 'ignore')
                                    except Exception:
                                        tstr = str(ctype)
                                else:
                                    tstr = str(ctype)
                                tl = tstr.lower()
                                is_num = any(k in tl for k in [
                                    'tinyint', 'smallint', 'mediumint', 'int', 'bigint',
                                    'decimal', 'numeric', 'float', 'double', 'bit'
                                ])
                                is_dt = any(k in tl for k in ['date', 'datetime', 'time', 'timestamp', 'year'])
                                is_str = any(k in tl for k in ['char', 'text', 'enum', 'set'])
                                is_blob = any(k in tl for k in ['blob', 'binary'])
                                
                                # Extract max length from column type for string columns
                                max_len = None
                                # For Navicat compatibility, we don't truncate data
                                # Only set max_len for very long text fields to prevent SQL syntax issues
                                if is_str:
                                    import re
                                    match = re.search(r'(\d+)', tstr)
                                    if match:
                                        try:
                                            max_len = int(match.group(1))
                                            # For Navicat compatibility, only truncate extremely long values (> 10000 chars)
                                            if max_len <= 10000:
                                                max_len = None  # Don't truncate at all
                                        except Exception:
                                            max_len = None
                                
                                col_names.append(name)
                                col_is_numeric.append(is_num)
                                col_is_datetime.append(is_dt)
                                col_is_stringy.append(is_str)
                                col_is_blob.append(is_blob)
                                col_max_lengths.append(max_len)
                            except Exception:
                                traceback.print_exc()
                        if not col_names:
                            col_names = []
                            col_is_numeric = []
                            col_is_datetime = []
                            col_is_stringy = []
                            col_is_blob = []
                            col_max_lengths = []
                        select_expr = ", ".join([f"CAST(`{c}` AS BINARY) AS `{c}`" for c in col_names]) if col_names else "*"
                        cur.execute(f"SELECT {select_expr} FROM `{t}`")
                        rows = cur.fetchall() or []
                        cols = [desc[0] for desc in cur.description]
                        cols = [(_as_text(c)) for c in cols]
                        if rows:
                            f.write("-- ----------------------------\n")
                            f.write(f"-- Records of {t}\n")
                            f.write("-- ----------------------------\n")
                            for r in rows:
                                out_vals = []
                                for idx, v in enumerate(r):
                                    is_num = col_is_numeric[idx] if idx < len(col_is_numeric) else False
                                    is_dt = col_is_datetime[idx] if idx < len(col_is_datetime) else False
                                    is_str = col_is_stringy[idx] if idx < len(col_is_stringy) else False
                                    is_bin = col_is_blob[idx] if idx < len(col_is_blob) else False
                                    max_len = col_max_lengths[idx] if idx < len(col_max_lengths) else None
                                    
                                    # For Navicat compatibility, use _escape for all values
                                    if is_bin:
                                        try:
                                            b = bytes(v) if isinstance(v, (bytes, bytearray)) else str(v).encode('utf-8', 'ignore')
                                            out_vals.append('0x' + b.hex())
                                        except Exception:
                                            out_vals.append('\'\'')
                                    else:
                                        # For all other types (numeric, datetime, string), use _escape
                                        # decode text with tis-620 -> utf-8 -> latin-1 fallback (Navicat order)
                                        s = None
                                        if isinstance(v, (bytes, bytearray)):
                                            b = bytes(v)
                                            for enc in ('tis-620', 'utf-8', 'latin-1', 'cp874'):
                                                try:
                                                    s = b.decode(enc)
                                                    break
                                                except Exception:
                                                    s = None
                                        else:
                                            s = str(v)
                                        
                                        # Handle string 'None' values - convert to empty string
                                        if s == 'None':
                                            s = ''
                                        
                                        # Use the enhanced _escape method with max_length (if any)
                                        escaped = self._escape(s, max_len)
                                        out_vals.append(escaped)
                                values = ", ".join(out_vals)
                                f.write(f"INSERT INTO `{t}` VALUES ({values});\n")
                done += 1
                pct = int(done * 100 / total_items)
                self.progress_changed.emit(pct)

            # Backup views
            for vname in views:
                if self._stop:
                    self.log_line.emit("หยุดโดยผู้ใช้")
                    self.ask_ui_reset.emit()
                    return
                try:
                    self.log_line.emit(f"[{done+1}/{total_items}] กำลังสำรองวิว: {vname}")
                except Exception:
                    pass
                view_file = os.path.join(tmp_dir, f"view_{vname}.sql")
                with open(view_file, "w", encoding="utf-8") as f:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write("/*\n")
                    f.write("Navicat MySQL Data Transfer\n\n")
                    f.write(f"Source Server         : {source_server}\n")
                    f.write(f"Source Server Version : {source_version}\n")
                    f.write(f"Source Host           : {source_host_line}\n")
                    f.write(f"Source Database       : {self._db_config.get('database') or ''}\n\n")
                    f.write("Target Server Type    : MYSQL\n")
                    f.write(f"Target Server Version : {source_version}\n")
                    f.write("File Encoding         : 65001\n\n")
                    f.write(f"Date: {now_str}\n")
                    f.write("*/\n\n")
                    f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                    f.write("-- ----------------------------\n")
                    f.write(f"-- View structure for {vname}\n")
                    f.write("-- ----------------------------\n")
                    with conn.cursor() as cur:
                        cur.execute(f"SHOW CREATE VIEW `{vname}`")
                        rowv = cur.fetchone()
                        vsql = rowv[1] if rowv and len(rowv) > 1 else None
                        if isinstance(vsql, (bytes, bytearray)):
                            try:
                                vsql = bytes(vsql).decode('utf-8', 'ignore')
                            except Exception:
                                vsql = None
                        if vsql:
                            f.write(f"DROP VIEW IF EXISTS `{vname}`;\n")
                            f.write(vsql + ";\n")
                done += 1
                pct = int(done * 100 / total_items)
                self.progress_changed.emit(pct)

            # Backup routines (procedures/functions)
            for rname, rtype in routines:
                if self._stop:
                    self.log_line.emit("หยุดโดยผู้ใช้")
                    self.ask_ui_reset.emit()
                    return
                rtype_u = (rtype or '').upper()
                label = 'โปรซีเยอร์' if rtype_u == 'PROCEDURE' else 'ฟังก์ชัน'
                try:
                    self.log_line.emit(f"[{done+1}/{total_items}] กำลังสำรอง{label}: {rname}")
                except Exception:
                    pass
                ext = 'proc' if rtype_u == 'PROCEDURE' else 'func'
                fn = os.path.join(tmp_dir, f"{ext}_{rname}.sql")
                with open(fn, "w", encoding="utf-8") as f:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write("/*\n")
                    f.write("Navicat MySQL Data Transfer\n\n")
                    f.write(f"Source Server         : {source_server}\n")
                    f.write(f"Source Server Version : {source_version}\n")
                    f.write(f"Source Host           : {source_host_line}\n")
                    f.write(f"Source Database       : {self._db_config.get('database') or ''}\n\n")
                    f.write("Target Server Type    : MYSQL\n")
                    f.write(f"Target Server Version : {source_version}\n")
                    f.write("File Encoding         : 65001\n\n")
                    f.write(f"Date: {now_str}\n")
                    f.write("*/\n\n")
                    f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                    with conn.cursor() as cur:
                        if rtype_u == 'PROCEDURE':
                            cur.execute(f"SHOW CREATE PROCEDURE `{rname}`")
                        else:
                            cur.execute(f"SHOW CREATE FUNCTION `{rname}`")
                        rr = cur.fetchone()
                        # SHOW CREATE returns columns: Procedure/Function, sql_mode, Create Procedure/Function, character_set_client, collation_connection, Database Collation
                        rsql = None
                        if rr and len(rr) >= 3:
                            rsql = rr[2]
                        if isinstance(rsql, (bytes, bytearray)):
                            try:
                                rsql = bytes(rsql).decode('utf-8', 'ignore')
                            except Exception:
                                rsql = None
                        if rsql:
                            if rtype_u == 'PROCEDURE':
                                f.write(f"DROP PROCEDURE IF EXISTS `{rname}`;\n")
                            else:
                                f.write(f"DROP FUNCTION IF EXISTS `{rname}`;\n")
                            f.write("DELIMITER ;;\n")
                            f.write(rsql + ";;\n")
                            f.write("DELIMITER ;\n")
                done += 1
                pct = int(done * 100 / total_items)
                self.progress_changed.emit(pct)
            zip_dir = os.path.dirname(self._zip_path)
            os.makedirs(zip_dir, exist_ok=True)
            with zipfile.ZipFile(self._zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for name in os.listdir(tmp_dir):
                    p = os.path.join(tmp_dir, name)
                    if os.path.isfile(p):
                        zf.write(p, arcname=name)
            
            self.log_line.emit("Navicat-style backup completed successfully")
            self.finished_ok.emit(self._zip_path)
        except Exception as e:
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
