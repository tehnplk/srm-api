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
)


class Patient(QWidget, Patient_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.settings = QSettings("SRM_API", "MySQL_Settings")

        # Wire events
        self.refresh_button.clicked.connect(self.load_patients)
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
        headers_with_check = ["check"] + headers
        # Remember cid column index for context menu copy
        try:
            self.cid_col = headers_with_check.index("cid")
        except ValueError:
            self.cid_col = -1
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
        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
        if chosen == act_copy:
            value = index.data()
            if value is not None:
                QGuiApplication.clipboard().setText(str(value))

    def _read_token(self) -> str:
        import os
        token_file = os.path.join(os.environ['USERPROFILE'], 'SRM Smart Card Single Sign-On', 'token.txt')
        with open(token_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('access-token='):
                    return line.split('=', 1)[1]
        raise ValueError('ไม่พบ access-token ในไฟล์ token.txt')

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

        if not rows:
            QMessageBox.information(self, 'ไม่มีข้อมูล', 'ไม่มีข้อมูลสำหรับตรวจสอบสิทธิ')
            return

        # Prepare worker thread
        token = read_token()
        cfg = self._get_db_config()

        class RightsWorker(QObject):
            progress_row = pyqtSignal(int)
            mark_checked = pyqtSignal(int)
            finished_summary = pyqtSignal(int, int, int, int, bool)  # skipped_today, skipped_dead, succeeded, failed, token_expired
            def __init__(self):
                super().__init__()
                self._stop = False
            def request_stop(self):
                self._stop = True

            def run(self):
                import pymysql
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
                            break
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
                            if isinstance(death_date, str) and death_date.strip():
                                update_patient_death(db_conn, cid)
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

        self._thread = QThread(self)
        self._worker = RightsWorker()
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

        def on_mark_checked(proxy_row: int):
            chk_idx = self.proxy.mapToSource(self.proxy.index(proxy_row, 0))
            item = self.proxy.sourceModel().item(chk_idx.row(), 0)
            if item and item.isCheckable():
                item.setCheckState(Qt.CheckState.Checked)

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
                QMessageBox.warning(self, 'สรุปการตรวจสอบสิทธิ', summary_text + "\n\nหยุดเนื่องจาก Token หมดอายุ")
            else:
                QMessageBox.information(self, 'สรุปการตรวจสอบสิทธิ', summary_text)
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

        self._thread.start()

        # Stop worker on app quit
        app = QCoreApplication.instance()
        if app is not None:
            try:
                app.aboutToQuit.disconnect(self._on_about_to_quit)
            except Exception:
                pass
            app.aboutToQuit.connect(self._on_about_to_quit)

    def _on_about_to_quit(self):
        self._stop_worker()

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

