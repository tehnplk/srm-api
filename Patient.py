import sys
from typing import List, Any

from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox, QInputDialog, QMenu, QAbstractItemView
from PyQt6.QtCore import QSettings, Qt, QSortFilterProxyModel, QRegularExpression, QObject, pyqtSignal, QThread, QCoreApplication, QTimer
from PyQt6.QtGui import QGuiApplication
from datetime import datetime
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from Patient_ui import Patient_ui
from srm import (
    read_token,
    ensure_srm_check_table,
    was_checked_today,
    is_patient_dead,
    upsert_srm_check,
    update_patient_death,
    call_right_search,
    refresh_token,
)


class Patient(QWidget, Patient_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.settings = QSettings("SRM_API", "MySQL_Settings")

        # Wire events
        self.refresh_button.clicked.connect(self.on_refresh_token)
        # Header context menu for filtering
        header = self.table.horizontalHeader()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self.on_header_context_menu)

        # Table context menu for copy actions
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_table_context_menu)

        # Initial load
        self.load_patients()
        # After load, mark rows already checked today
        try:
            self.proxy.modelReset.connect(self._mark_checked_today_in_view)
        except Exception:
            pass
        QTimer.singleShot(0, self._mark_checked_today_in_view)

        # Wire rights check button
        self.check_rights_button.clicked.connect(self.check_rights)
        # Wire stop button
        try:
            self.stop_rights_button.clicked.connect(self.on_stop_rights)
        except Exception:
            pass

    def _get_db_config(self):
        return {
            "host": self.settings.value("host", "localhost"),
            "port": int(self.settings.value("port", 3306)),
            "user": self.settings.value("user", ""),
            "password": self.settings.value("password", ""),
            "database": self.settings.value("database", ""),
            "charset": "tis620",
            "connect_timeout": int(self.settings.value("timeout", 10)),
        }

    def _ensure_config_complete(self) -> bool:
        cfg = self._get_db_config()
        missing = [k for k in ("host", "user", "database") if not str(cfg.get(k, "")).strip()]
        if missing:
            QMessageBox.warning(self, "การตั้งค่าไม่ครบ", f"โปรดตั้งค่า: {', '.join(missing)} ในเมนู ตั้งค่า")
            return False
        return True

    def load_patients(self):
        if not self._ensure_config_complete():
            return
        import pymysql

        cfg = self._get_db_config()
        conn = pymysql.connect(**cfg)
        with conn.cursor() as cur:
            system = str(self.settings.value("system", "jhcis")).strip().lower()
            if system == "jhcis":
                # JHCIS: map to expected headers, join ctitle to resolve prename title
                cur.execute(
                    """
                    SELECT 
                        p.idcard          AS cid,
                        t.titlename       AS pname,
                        p.fname           AS fname,
                        p.lname           AS lname,
                        p.rightcode       AS pttype,
                        p.rightno         AS pttype_no
                    FROM person p
                    LEFT JOIN ctitle t ON p.prename = t.titlecode
                    WHERE CHAR_LENGTH(p.idcard) = 13 
                      AND p.idcard REGEXP '^[0-9]{13}$'
                      AND (p.dischargedate IS NULL OR p.dischargedate = '0000-00-00')
                    """
                )
            else:
                # HOSxP default
                dead_cids = []
                try:
                    if _has_hosxp_death_flag(conn):
                        cur.execute(
                            """
                            SELECT cid FROM patient
                            WHERE death='Y' AND CHAR_LENGTH(cid)=13 AND cid REGEXP '^[0-9]{13}$'
                            """
                        )
                        dead_cids = [str(r[0]) for r in (cur.fetchall() or []) if r and r[0]]
                except Exception:
                    dead_cids = []

                if dead_cids:
                    placeholders = ",".join(["%s"] * len(dead_cids))
                    sql = (
                        """
                        SELECT cid, pname, fname, lname, pttype, pttype_no
                        FROM patient
                        WHERE CHAR_LENGTH(cid) = 13 AND cid REGEXP '^[0-9]{13}$'
                          AND cid NOT IN (""" + placeholders + ")"
                    )
                    cur.execute(sql, dead_cids)
                else:
                    cur.execute(
                        """
                        SELECT cid, pname, fname, lname, pttype, pttype_no
                        FROM patient
                        WHERE CHAR_LENGTH(cid) = 13 AND cid REGEXP '^[0-9]{13}$'
                        """
                    )
            rows = cur.fetchall()
            headers = [col[0] for col in cur.description]
        conn.close()

        self._populate_table(headers, rows)

    def _populate_table(self, headers: List[str], rows: List[tuple]):
        # Prepend a 'check' column
        headers_with_check = ["check"] + headers + ["pttype_new", "pttype_no_new"]
        # Remember cid column index for context menu copy
        try:
            self.cid_col = headers_with_check.index("cid")
        except ValueError:
            self.cid_col = -1
        # Remember new columns indices for later updates
        try:
            self.pttype_new_col = headers_with_check.index("pttype_new")
        except ValueError:
            self.pttype_new_col = -1
        try:
            self.pttype_no_new_col = headers_with_check.index("pttype_no_new")
        except ValueError:
            self.pttype_no_new_col = -1
        model = QStandardItemModel()
        model.setColumnCount(len(headers_with_check))
        model.setHorizontalHeaderLabels(headers_with_check)

        for r in rows:
            items: List[QStandardItem] = []
            # Checkbox item
            chk = QStandardItem()
            chk.setCheckable(True)
            chk.setCheckState(Qt.CheckState.Unchecked)
            chk.setEditable(False)
            items.append(chk)
            for val in r:
                if val is None:
                    text = ""
                else:
                    try:
                        text = str(val)
                    except Exception:
                        text = repr(val)
                it = QStandardItem(text)
                items.append(it)
            # Append placeholders for new columns
            items.append(QStandardItem(""))
            items.append(QStandardItem(""))
            model.appendRow(items)

        # Assign model via proxy for filtering/sorting
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.table.setModel(self.proxy)

    def on_header_context_menu(self, pos):
        header = self.table.horizontalHeader()
        logicalIndex = header.logicalIndexAt(pos)
        if logicalIndex < 0:
            return
        menu = QMenu(self)
        act_filter = menu.addAction("Filter...")
        act_clear = menu.addAction("Clear filter")
        chosen = menu.exec(header.mapToGlobal(pos))
        if chosen == act_filter:
            # ignore checkbox column
            if logicalIndex == 0:
                return
            title = self.proxy.headerData(logicalIndex, Qt.Orientation.Horizontal)
            text, ok = QInputDialog.getText(self, "กรองข้อมูล", f"คำที่ต้องการกรองในคอลัมน์: {title}")
            if not ok:
                return
            self.proxy.setFilterKeyColumn(logicalIndex)
            if text.strip():
                self.proxy.setFilterRegularExpression(QRegularExpression(text))
            else:
                self.proxy.setFilterRegularExpression("")
        elif chosen == act_clear:
            self.proxy.setFilterRegularExpression("")

    def on_table_context_menu(self, pos):
        if getattr(self, 'cid_col', -1) < 0:
            return
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        # Only show menu when right-click is on CID column
        if index.column() != self.cid_col:
            return
        menu = QMenu(self)
        act_copy = menu.addAction("Copy CID")
        act_check_single = menu.addAction("ตรวจสอบสิทธิ")
        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
        if chosen == act_copy:
            value = index.data()
            if value is not None:
                QGuiApplication.clipboard().setText(str(value))
        elif chosen == act_check_single:
            # Trigger rights check for this single CID
            value = index.data()
            if value is not None:
                try:
                    proxy_row = index.row()
                    self._start_rights_worker([(proxy_row, str(value))], debug=True)
                except Exception:
                    pass

    def _read_token(self) -> str:
        import os
        token_file = os.path.join(os.environ['USERPROFILE'], 'SRM Smart Card Single Sign-On', 'token.txt')
        with open(token_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('access-token='):
                    return line.split('=', 1)[1]
        raise ValueError('ไม่พบ access-token ในไฟล์ token.txt')

    def on_refresh_token(self):
        try:
            new_tok = refresh_token()
            QMessageBox.information(self, 'สำเร็จ', 'รีเฟรชโทเคนเรียบร้อยแล้ว')
        except Exception:
            QMessageBox.warning(self, 'ล้มเหลว', 'การขอ token ใหม่เกิดข้อผิดพลาด')

    def _start_rights_worker(self, rows: List[tuple], debug: bool = False):
        import pymysql
        
        # Determine cid column in proxy coordinates
        if getattr(self, 'cid_col', -1) < 0:
            QMessageBox.warning(self, 'ไม่พบคอลัมน์', 'ไม่พบคอลัมน์ cid ในผลลัพธ์')
            return
        if not rows:
            QMessageBox.information(self, 'ไม่มีข้อมูล', 'ไม่มีข้อมูลสำหรับตรวจสอบสิทธิ')
            return

        # Prepare worker thread
        try:
            token = read_token()
        except Exception:
            try:
                self._show_status('การขอ token ใหม่เกิดข้อผิดพลาด', 7000)
            except Exception:
                pass
            return
        cfg = self._get_db_config()

        class RightsWorker(QObject):
            progress_row = pyqtSignal(int)
            mark_checked = pyqtSignal(int)
            finished_summary = pyqtSignal(int, int, int, int, bool)  # skipped_today, skipped_dead, succeeded, failed, token_expired
            need_resume_from = pyqtSignal(int)  # row index to resume from when token expired
            update_rights = pyqtSignal(int, str, str, str)  # proxy_row, cid, pttype_new, pttype_no_new
            debug_output = pyqtSignal(str, str)  # cid, text
            def __init__(self, debug: bool = False):
                super().__init__()
                self._stop = False
                self._debug = bool(debug)
            def request_stop(self):
                self._stop = True

            def run(self):
                import pymysql
                import json
                db_conn = pymysql.connect(**cfg)
                ensure_srm_check_table(db_conn)
                skipped_today = 0
                skipped_dead = 0
                succeeded = 0
                failed = 0
                token_expired = False
                try:
                    for proxy_row, cid in rows:
                        if self._stop:
                            break
                        try:
                            self.progress_row.emit(proxy_row)
                        except RuntimeError:
                            break
                        if is_patient_dead(db_conn, cid):
                            skipped_dead += 1
                            continue
                        if was_checked_today(db_conn, cid):
                            try:
                                self.mark_checked.emit(proxy_row)
                            except RuntimeError:
                                break
                            skipped_today += 1
                            continue
                        resp = call_right_search(token, cid)
                        # print(cid, resp.json())  # optional debug
                        if resp.status_code == 401:
                            token_expired = True
                            try:
                                self.need_resume_from.emit(proxy_row)
                            except RuntimeError:
                                pass
                            break
                        if self._debug:
                            try:
                                print(f"[DEBUG] CID={cid} status={resp.status_code}")
                                try:
                                    js = json.dumps(resp.json(), ensure_ascii=False)
                                    print(js)
                                    try:
                                        self.debug_output.emit(str(cid), js)
                                    except Exception:
                                        pass
                                except Exception:
                                    txt = resp.text
                                    print(txt)
                                    try:
                                        self.debug_output.emit(str(cid), txt)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                        if resp.status_code == 200:
                            try:
                                self.mark_checked.emit(proxy_row)
                            except RuntimeError:
                                break
                            try:
                                data = resp.json()
                            except Exception:
                                data = {}
                            check_date = data.get('checkDate')
                            funds = data.get('funds', [])
                            death_date = data.get('deathDate')
                            upsert_srm_check(db_conn, cid, check_date, death_date, funds, resp.status_code)
                            # Determine new pttype values directly from API response with fallbacks to funds[]
                            new_type = ""
                            new_no = ""
                            try:
                                # Prefer top-level fields if available
                                subinscl_top = data.get('subinscl') or data.get('subInscl')
                                cardid_top = data.get('cardId') or data.get('cardID')
                                if subinscl_top:
                                    if isinstance(subinscl_top, dict):
                                        new_type = str(subinscl_top.get('id') or subinscl_top.get('name') or "")
                                    else:
                                        new_type = str(subinscl_top)
                                if cardid_top:
                                    new_no = str(cardid_top)

                                # Fallback to first fund entry when top-level missing
                                if (not new_type or not new_no) and isinstance(funds, list) and funds:
                                    f0 = funds[0] if isinstance(funds[0], dict) else {}
                                    if not new_type:
                                        sub = f0.get('subInscl') if isinstance(f0.get('subInscl'), dict) else None
                                        if sub:
                                            new_type = str(sub.get('id') or sub.get('name') or "")
                                    if not new_no:
                                        new_no = str(f0.get('cardId') or f0.get('cardID') or "")
                            except Exception:
                                new_type = ""
                                new_no = ""
                            try:
                                self.update_rights.emit(proxy_row, cid, new_type, new_no)
                            except RuntimeError:
                                pass
                            if isinstance(death_date, str) and death_date.strip():
                                try:
                                    _update_patient_death_from_api(db_conn, cid, death_date)
                                except Exception:
                                    # fail-soft; do not block the loop
                                    pass
                            succeeded += 1
                        else:
                            failed += 1
                            continue
                finally:
                    try:
                        db_conn.close()
                    except Exception:
                        pass
                    try:
                        if not self._stop:
                            self.finished_summary.emit(skipped_today, skipped_dead, succeeded, failed, token_expired)
                    except RuntimeError:
                        pass

        # Remember rows for potential retry (e.g., token refresh)
        try:
            self._pending_rows = list(rows)
        except Exception:
            self._pending_rows = rows
        self._pending_debug = bool(debug)

        self._thread = QThread(self)
        self._worker = RightsWorker(debug=debug)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)

        # UI slots
        def on_progress_row(proxy_row: int):
            idx = self.proxy.index(proxy_row, self.cid_col)
            try:
                self.table.selectRow(idx.row())
                self.table.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)
            except Exception:
                pass
            try:
                # Track current processing row for stop/resume
                self._current_processing_row = int(proxy_row)
            except Exception:
                self._current_processing_row = proxy_row

        def on_mark_checked(proxy_row: int):
            chk_idx = self.proxy.mapToSource(self.proxy.index(proxy_row, 0))
            item = self.proxy.sourceModel().item(chk_idx.row(), 0)
            if item and item.isCheckable():
                item.setCheckState(Qt.CheckState.Checked)

        def on_update_rights(proxy_row: int, cid: str, pttype_new: str, pttype_no_new: str):
            try:
                # Find current proxy rows that match this CID to avoid stale proxy_row issues
                rows_to_update = []
                for r in range(self.proxy.rowCount()):
                    idx = self.proxy.index(r, self.cid_col)
                    if str(idx.data()) == str(cid):
                        rows_to_update.append(r)
                if not rows_to_update:
                    rows_to_update = [proxy_row]
                for pr in rows_to_update:
                    if getattr(self, 'pttype_new_col', -1) >= 0:
                        src_idx_type = self.proxy.mapToSource(self.proxy.index(pr, self.pttype_new_col))
                        item_type = self.proxy.sourceModel().item(src_idx_type.row(), self.pttype_new_col)
                        if item_type:
                            item_type.setText(pttype_new or "")
                    if getattr(self, 'pttype_no_new_col', -1) >= 0:
                        src_idx_no = self.proxy.mapToSource(self.proxy.index(pr, self.pttype_no_new_col))
                        item_no = self.proxy.sourceModel().item(src_idx_no.row(), self.pttype_no_new_col)
                        if item_no:
                            item_no.setText(pttype_no_new or "")
            except Exception:
                pass

        def on_finished_summary(skipped_today: int, skipped_dead: int, succeeded: int, failed: int, token_expired: bool):
            total_rows = self.proxy.rowCount()
            summary_lines = [
                f"ทั้งหมด: {total_rows}",
                f"ข้าม (ตรวจแล้ววันนี้): {skipped_today}",
                f"ข้าม (เสียชีวิต): {skipped_dead}",
                f"สำเร็จ: {succeeded}",
                f"ล้มเหลว: {failed}",
            ]
            summary_text = "\n".join(summary_lines)
            if token_expired:
                # Notify token expired via status bar
                try:
                    self._show_status("Token หมดอายุ กำลังรีเฟรชโทเคนอัตโนมัติ...", 7000)
                except Exception:
                    pass
                # Retry guard to avoid infinite loops
                if not hasattr(self, '_retry_after_refresh'):
                    self._retry_after_refresh = False
                if not self._retry_after_refresh:
                    self._retry_after_refresh = True
                    try:
                        # Refresh token now
                        from srm import refresh_token
                        refresh_token()
                    except Exception:
                        try:
                            self._show_status('การขอ token ใหม่เกิดข้อผิดพลาด', 7000)
                        except Exception:
                            pass
                    else:
                        # Continue after 5 seconds with the same pending rows
                        try:
                            self._show_status('รีเฟรชโทเคนสำเร็จ กำลังตรวจสอบสิทธิต่อใน 5 วินาที...', 7000)
                        except Exception:
                            pass
                        QTimer.singleShot(5000, lambda: self._start_rights_worker(getattr(self, '_pending_rows', []), debug=getattr(self, '_pending_debug', False)))
                else:
                    try:
                        self._show_status('พยายามรีเฟรชโทเคนแล้ว แต่ยังหมดอายุอยู่ ไม่ทำการลองซ้ำอีกครั้ง', 7000)
                    except Exception:
                        pass
            else:
                # Reset resume and retry flags on successful completion
                try:
                    self._resume_from = 0
                    self._retry_after_refresh = False
                except Exception:
                    pass
                try:
                    self._show_status('ตรวจสอบสิทธิเสร็จสิ้น', 5000)
                except Exception:
                    pass
            self._thread.quit()
            self._thread.wait()
            # Let Qt delete objects on thread finish; guard double-deletes
            try:
                self._worker.deleteLater()
            except Exception:
                pass
            try:
                self._thread.deleteLater()
            except Exception:
                pass

        self._worker.progress_row.connect(on_progress_row)
        self._worker.mark_checked.connect(on_mark_checked)
        self._worker.finished_summary.connect(on_finished_summary)
        self._worker.update_rights.connect(on_update_rights)
        def on_debug_output(cid: str, text: str):
            try:
                # Truncate very long outputs for dialog
                preview = text if len(text) <= 4000 else (text[:4000] + "... [truncated]")
                QMessageBox.information(self, f"API Response (CID: {cid})", preview)
            except Exception:
                pass
        self._worker.debug_output.connect(on_debug_output)
        def on_need_resume_from(proxy_row: int):
            try:
                self._resume_from = int(proxy_row)
            except Exception:
                self._resume_from = 0
        self._worker.need_resume_from.connect(on_need_resume_from)

        self._thread.start()

        # Stop worker on app quit
        app = QCoreApplication.instance()
        if app is not None:
            try:
                app.aboutToQuit.disconnect(self._on_about_to_quit)
            except Exception:
                pass
            app.aboutToQuit.connect(self._on_about_to_quit)

    def on_stop_rights(self):
        # Set resume position to the current processing row, if known
        try:
            if hasattr(self, '_current_processing_row'):
                self._resume_from = int(self._current_processing_row)
        except Exception:
            pass
        # Stop the background worker and thread
        self._stop_worker()
        try:
            self._show_status('หยุดการตรวจสอบสิทธิแล้ว', 4000)
        except Exception:
            pass

    def check_rights(self):
        import pymysql

        # Determine cid column in proxy coordinates
        if getattr(self, 'cid_col', -1) < 0:
            QMessageBox.warning(self, 'ไม่พบคอลัมน์', 'ไม่พบคอลัมน์ cid ในผลลัพธ์')
            return

        # Build list of cids from current proxy model (proxy order)
        rows = []
        for row in range(self.proxy.rowCount()):
            idx = self.proxy.index(row, self.cid_col)
            val = idx.data()
            if val:
                rows.append((row, str(val)))

        # Determine resume position if any (continue from where stopped)
        start_from = getattr(self, '_resume_from', 0)
        if isinstance(start_from, int) and start_from > 0:
            rows = [(pr, cid) for pr, cid in rows if pr >= start_from]

        self._start_rights_worker(rows)

    def _on_about_to_quit(self):
        self._stop_worker()

    def _show_status(self, text: str, timeout_ms: int = 5000):
        try:
            p = self.parent()
            if p is not None and hasattr(p, 'statusbar') and p.statusbar is not None:
                p.statusbar.showMessage(str(text), int(timeout_ms))
        except Exception:
            pass

    def _stop_worker(self):
        if hasattr(self, '_worker') and self._worker is not None:
            try:
                self._worker.request_stop()
            except Exception:
                pass
        if hasattr(self, '_thread') and self._thread is not None:
            try:
                self._thread.quit()
                self._thread.wait(3000)
            except Exception:
                pass

    # --- DB helpers for death update ---
    def _column_exists(self, conn, table: str, column: str) -> bool:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s
                    """,
                    (table, column),
                )
                return cur.fetchone() is not None
        except Exception:
            return False

    def _update_patient_death_from_api(self, conn, cid: str, death_date: str):
        if not (isinstance(death_date, str) and death_date.strip()):
            return
        # Normalize death_date to YYYY-MM-DD
        dd = death_date.strip()
        try:
            if len(dd) > 10:
                dd = dd[:10]
        except Exception:
            pass
        # Build SET clause depending on column existence
        sets = ["death='Y'", "deathday=%s"]
        params = [dd, cid]
        has_lastupdate = self._column_exists(conn, 'patient', 'lastupdate')
        has_last_update = self._column_exists(conn, 'patient', 'last_update')
        if has_lastupdate:
            sets.append("lastupdate=NOW()")
        if has_last_update:
            sets.append("last_update=NOW()")
        sql = f"UPDATE patient SET {', '.join(sets)} WHERE cid=%s"
        with conn.cursor() as cur:
            cur.execute(sql, params)
        try:
            conn.commit()
        except Exception:
            pass

    def closeEvent(self, event):
        # Ensure background thread is stopped when window closes
        self._stop_worker()
        super().closeEvent(event)

    def _mark_checked_today_in_view(self):
        # Batch query srm_check for today's checked CIDs and tick the checkbox in column 0
        try:
            row_count = self.proxy.rowCount()
            if row_count == 0:
                return
            # Collect CIDs and map cid -> list of proxy rows
            cid_rows = {}
            for r in range(row_count):
                idx = self.proxy.index(r, self.cid_col)
                cid = idx.data()
                if cid:
                    cid_rows.setdefault(str(cid), []).append(r)
            if not cid_rows:
                return
            # Query in batches
            import pymysql
            cfg = self._get_db_config()
            conn = pymysql.connect(**cfg)
            ensure_srm_check_table(conn)
            checked_today = set()
            cids = list(cid_rows.keys())
            B = 500
            with conn.cursor() as cur:
                for i in range(0, len(cids), B):
                    chunk = cids[i:i+B]
                    placeholders = ",".join(["%s"] * len(chunk))
                    sql = f"SELECT cid FROM srm_check WHERE DATE(check_date)=CURDATE() AND cid IN ({placeholders})"
                    cur.execute(sql, chunk)
                    for row in cur.fetchall() or []:
                        checked_today.add(str(row[0]))
            try:
                conn.close()
            except Exception:
                pass
            if not checked_today:
                return
            # Tick checkboxes for matched rows
            for cid, proxy_rows in cid_rows.items():
                if cid in checked_today:
                    for pr in proxy_rows:
                        chk_idx = self.proxy.mapToSource(self.proxy.index(pr, 0))
                        item = self.proxy.sourceModel().item(chk_idx.row(), 0)
                        if item and item.isCheckable():
                            item.setCheckState(Qt.CheckState.Checked)
        except Exception:
            # Fail silently to avoid blocking UI
            pass

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Patient()
    window.show()
    sys.exit(app.exec())

# Helper: mark already-checked-today rows
def _safe_iter(val):
    try:
        return iter(val)
    except Exception:
        return iter(())

