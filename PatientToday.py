import sys
import traceback
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox, QMenu, QAbstractItemView, QInputDialog
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
from PyQt6.QtCore import QDate, QLocale, Qt, QObject, QThread, pyqtSignal, QSortFilterProxyModel, QTimer, QCoreApplication, QRegularExpression
from srm import (
    read_token,
    ensure_srm_check_table,
    upsert_srm_check,
    call_right_search,
    was_checked_today,
    is_patient_dead,
    refresh_token,
    open_srm_program,
)

from PatientToday_ui import PatientToday_ui


class PatientToday(QWidget, PatientToday_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Initialize date picker to today and wire change handler
        try:
            self.date_edit.setDate(QDate.currentDate())
        except Exception as e:
            traceback.print_exc()
        # Force Gregorian year and Western digits (avoid Thai/Buddhist year and numerals)
        try:
            en_us = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
            self.date_edit.setLocale(en_us)
            cw = self.date_edit.calendarWidget()
            if cw is not None:
                cw.setLocale(en_us)
        except Exception as e:
            traceback.print_exc()
        try:
            self.date_edit.dateChanged.connect(self.on_date_changed)
        except Exception as e:
            traceback.print_exc()

        # Initial load
        try:
            self._load_for_date(self.date_edit.date())
        except Exception as e:
            traceback.print_exc()

        # Setup context menu for copying vn/cid (set up once)
        try:
            self.vn_col = 0
            self.cid_col = 1
            # Table (alias to Patient's naming already in UI)
            self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.on_table_context_menu)
            # Header filter menu like Patient
            header = self.table.horizontalHeader()
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(self.on_header_context_menu)
            # Match Patient selection UX
            self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            # Buttons mirror Patient: single toggle button (no separate stop button)
            self.stop_rights_button.setVisible(False)
            self._is_checking = False
            self.check_rights_button.clicked.connect(self.on_toggle_check_rights)
            # Do not show or wire a separate stop button
            self.refresh_button.clicked.connect(self.on_refresh_token)
        except Exception as e:
            traceback.print_exc()

    def on_date_changed(self, qdate: QDate):
        # Placeholder: handle date change (e.g., reload table data for selected date)
        # Keep UI responsive without modal dialogs here
        try:
            self._load_for_date(qdate)
        except Exception as e:
            QMessageBox.warning(self, "โหลดข้อมูลไม่สำเร็จ", str(e))

    def _get_db_config(self) -> dict:
        from PyQt6.QtCore import QSettings
        settings = QSettings("SRM_API", "MySQL_Settings")
        return {
            "host": settings.value("host", "localhost"),
            "port": int(settings.value("port", 3306)),
            "user": settings.value("user", ""),
            "password": settings.value("password", ""),
            "database": settings.value("database", ""),
            "charset": "tis620",
            "connect_timeout": int(settings.value("timeout", 10)),
        }

    def _get_system(self) -> str:
        from PyQt6.QtCore import QSettings
        settings = QSettings("SRM_API", "MySQL_Settings")
        return str(settings.value("system", "jhcis")).strip().lower()

    def _load_for_date(self, qdate: QDate):
        import pymysql
        cfg = self._get_db_config()
        if not str(cfg.get("host", "")).strip() or not str(cfg.get("user", "")).strip() or not str(cfg.get("database", "")).strip():
            raise ValueError("โปรดตั้งค่าการเชื่อมต่อฐานข้อมูลให้ครบถ้วนในเมนู ตั้งค่า")

        date_str = qdate.toString("yyyy-MM-dd")
        system = self._get_system()

        if system == 'hosxp':
            sql = (
                """
                SELECT 
                    p.cid,
                    p.pname,
                    p.fname,
                    p.lname,
                    COALESCE(o.pttype, p.pttype) AS pttype,
                    COALESCE(o.pttypeno, p.pttype_no) AS pttype_no,
                    p.last_update AS last_update_right
                FROM ovst o
                JOIN patient p ON p.hn = o.hn
                WHERE DATE(o.vstdate) = %s
                ORDER BY o.vn
                """
            )
            params = (date_str,)
        else:
            # JHCIS: list by visit table
            sql = (
                """
                SELECT 
                    p.idcard AS cid,
                    t.titlename AS pname,
                    p.fname AS fname,
                    p.lname AS lname,
                    COALESCE(v.rightcode, p.rightcode) AS pttype,
                    COALESCE(v.rightno, p.rightno) AS pttype_no,
                    COALESCE(v.dateupdate, p.dateupdate) AS last_update_right
                FROM visit v
                JOIN person p ON p.pid = v.pid
                LEFT JOIN ctitle t ON p.prename = t.titlecode
                WHERE v.visitdate = %s
                ORDER BY p.idcard
                """
            )
            params = (date_str,)

        rows = []
        headers = ["cid", "pname", "fname", "lname", "pttype", "pttype_no", "last_update_right"]
        conn = pymysql.connect(**cfg)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall() or []
        finally:
            try:
                conn.close()
            except Exception as e:
                traceback.print_exc()
        # Populate table model with fetched rows, matching Patient headers
        headers_with_check = ["check"] + headers + ["pttype_new", "pttype_no_new"]
        model = QStandardItemModel()
        model.setColumnCount(len(headers_with_check))
        model.setHorizontalHeaderLabels(headers_with_check)
        for r in rows:
            items = []
            chk = QStandardItem()
            chk.setCheckable(True)
            chk.setCheckState(Qt.CheckState.Unchecked)
            chk.setEditable(False)
            items.append(chk)
            for val in r:
                text = "" if val is None else str(val)
                it = QStandardItem(text)
                it.setEditable(False)
                items.append(it)
            # placeholders for new columns
            items.append(QStandardItem(""))
            items.append(QStandardItem(""))
            model.appendRow(items)
        # Assign via proxy to mirror Patient filtering/sorting behavior
        self.source_model = model
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.table.setModel(self.proxy)
        # Ensure cid column index is consistent with Patient (1 after check)
        self.cid_col = 1
        # Remember new columns index
        self.pttype_new_col = headers_with_check.index("pttype_new")
        self.pttype_no_new_col = headers_with_check.index("pttype_no_new")

    # ==== Patient-like controls ====
    def _show_status(self, msg: str, msec: int = 3000):
        try:
            print(f"[STATUS] {msg}")
        except Exception:
            pass

    def on_refresh_token(self):
        try:
            refresh_token()
            QMessageBox.information(self, 'สำเร็จ', 'รีเฟรชโทเคนเรียบร้อยแล้ว')
        except Exception as e:
            # Try to open SRM program
            try:
                if open_srm_program():
                    QMessageBox.warning(self, 'ล้มเหลว', f'{e}\n\nโปรด Login ใน SRM ด้วยบัตรประชาชนของเจ้าหน้าที่ตรวจสอบสิทธิ\n\nโปรแกรม SRM ถูกเปิดขึ้นมาแล้ว')
                else:
                    QMessageBox.warning(self, 'ล้มเหลว', f'{e}\n\nโปรด Login ใน SRM ด้วยบัตรประชาชนของเจ้าหน้าที่ตรวจสอบสิทธิ')
            except Exception:
                QMessageBox.warning(self, 'ล้มเหลว', f'{e}\n\nโปรด Login ใน SRM ด้วยบัตรประชาชนของเจ้าหน้าที่ตรวจสอบสิทธิ')

    def _set_checking_state(self, running: bool):
        self._is_checking = bool(running)
        try:
            self.check_rights_button.setText("❌ หยุดตรวจสอบ" if self._is_checking else "✅ ตรวจสอบสิทธิ")
            # Keep separate stop button hidden (single-button UX)
            self.stop_rights_button.setVisible(False)
        except Exception:
            pass

    def on_toggle_check_rights(self):
        if getattr(self, '_is_checking', False):
            self.on_stop_rights()
        else:
            self.check_rights()

    def on_stop_rights(self):
        try:
            if hasattr(self, '_worker') and self._worker is not None:
                if hasattr(self._worker, 'request_stop'):
                    self._worker.request_stop()
            # remember current row to resume from (retry this row)
            try:
                cur = int(getattr(self, '_current_processing_row', 0))
                self._resume_from = max(0, cur)
            except Exception:
                self._resume_from = getattr(self, '_current_processing_row', 0)
            # also stop the thread gracefully
            try:
                if hasattr(self, '_thread') and self._thread is not None and self._thread.isRunning():
                    self._thread.quit()
                    self._thread.wait(3000)
            except Exception:
                pass
        except Exception:
            pass
        self._set_checking_state(False)

    def check_rights(self):
        # Build row list (proxy_row, cid): prefer checked rows else all visible
        if not hasattr(self, 'proxy') or self.proxy is None:
            QMessageBox.information(self, 'ไม่มีข้อมูล', 'ไม่มีข้อมูลสำหรับตรวจสอบสิทธิ')
            return
        rows = []
        try:
            rc = self.proxy.rowCount()
            resume_from = int(getattr(self, '_resume_from', 0) or 0)
            # If resuming (user stopped previously), ignore checkboxes and continue from resume_from
            if resume_from > 0:
                start_pr = resume_from if (resume_from >= 0 and resume_from < rc) else 0
                for pr in range(start_pr, rc):
                    cid_val = self.proxy.index(pr, self.cid_col).data()
                    if cid_val:
                        rows.append((pr, str(cid_val)))
            else:
                # Normal flow: pass 1 collect checked rows (manual selection), else process all
                for pr in range(rc):
                    src_row = self.proxy.mapToSource(self.proxy.index(pr, 0)).row()
                    item = self.proxy.sourceModel().item(src_row, 0)
                    if item and item.isCheckable() and item.checkState() == Qt.CheckState.Checked:
                        cid_val = self.proxy.index(pr, self.cid_col).data()
                        if cid_val:
                            rows.append((pr, str(cid_val)))
                if not rows:
                    for pr in range(0, rc):
                        cid_val = self.proxy.index(pr, self.cid_col).data()
                        if cid_val:
                            rows.append((pr, str(cid_val)))
        except Exception:
            traceback.print_exc()
        if not rows:
            QMessageBox.information(self, 'ไม่มีข้อมูล', 'ไม่มีข้อมูลสำหรับตรวจสอบสิทธิ')
            return
        self._start_rights_worker(rows, debug=False, force=False)

    def _start_rights_worker(self, rows: list[tuple], debug: bool = False, force: bool = False):
        import pymysql
        if not rows:
            QMessageBox.information(self, 'ไม่มีข้อมูล', 'ไม่มีข้อมูลสำหรับตรวจสอบสิทธิ')
            return
        try:
            token = read_token()
        except Exception as e:
            traceback.print_exc()
            self._show_status('การขอ token ใหม่เกิดข้อผิดพลาด', 7000)
            return
        cfg = self._get_db_config()
        system = self._get_system()
        date_str = self.date_edit.date().toString('yyyy-MM-dd')
        auto_update = getattr(self, 'auto_update_checkbox', None) and self.auto_update_checkbox.isChecked()

        class RightsWorker(QObject):
            progress_row = pyqtSignal(int)
            mark_checked = pyqtSignal(int)
            finished_summary = pyqtSignal(int, int, int, int, bool)
            need_resume_from = pyqtSignal(int)
            update_rights = pyqtSignal(int, str, str, str)
            def __init__(self, system: str, date_str: str, debug: bool = False, force: bool = False, auto_update: bool = False):
                super().__init__()
                self._stop = False
                self._debug = bool(debug)
                self._force_recheck = bool(force)
                self._system = (system or '').lower()
                self._date = date_str
                self._auto_update = bool(auto_update)
            def request_stop(self):
                self._stop = True
            def _checked_on_date(self, conn, cid: str) -> bool:
                try:
                    with conn.cursor() as c:
                        c.execute("SELECT 1 FROM srm_check WHERE cid=%s AND DATE(check_date)=%s LIMIT 1", (cid, self._date))
                        r = c.fetchone()
                        return bool(r)
                except Exception:
                    return False
            def run(self):
                import pymysql, json
                db_conn = pymysql.connect(**cfg)
                ensure_srm_check_table(db_conn)
                skipped_today = 0; skipped_dead = 0; succeeded = 0; failed = 0; token_expired = False
                try:
                    for proxy_row, cid in rows:
                        if self._stop:
                            try:
                                print(f"[SKIP] CID={cid} reason=stop_requested")
                            except Exception:
                                pass
                            break
                        try:
                            self.progress_row.emit(proxy_row)
                        except RuntimeError:
                            break
                        # dead info (log only)
                        try:
                            if is_patient_dead(db_conn, cid):
                                print(f"[INFO] CID={cid} marked dead in DB; proceeding to call API as requested")
                                skipped_dead += 1
                        except Exception:
                            pass
                        # skip if already checked in selected date unless force
                        if (not self._force_recheck) and self._checked_on_date(db_conn, cid):
                            try:
                                self.mark_checked.emit(proxy_row)
                                print(f"[SKIP] CID={cid} reason=checked_on_date")
                            except Exception:
                                pass
                            skipped_today += 1
                            continue
                        resp = call_right_search(token, cid)
                        if self._debug:
                            try:
                                body_text = json.dumps(resp.json(), ensure_ascii=False)
                            except Exception:
                                body_text = resp.text
                            try:
                                print(f"[API] CID={cid} status={resp.status_code}")
                                print(body_text)
                            except Exception:
                                pass
                        if resp.status_code == 401:
                            token_expired = True
                            try:
                                print(f"[STOP] CID={cid} reason=token_expired (status=401), will refresh and resume")
                            except Exception:
                                pass
                            try:
                                self.need_resume_from.emit(proxy_row)
                            except RuntimeError:
                                pass
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
                            upsert_srm_check(db_conn, cid, check_date, None, funds, resp.status_code)
                            # extract minimal
                            new_type = ""; new_no = ""; hospmain_hcode=None; hospsub_hcode=None; begin_date=None; expire_date=None; main_inscl_name=None; sub_inscl_name=None
                            try:
                                subinscl_top = data.get('subinscl') or data.get('subInscl')
                                cardid_top = data.get('cardId') or data.get('cardID')
                                if isinstance(subinscl_top, dict):
                                    new_type = str(subinscl_top.get('id') or subinscl_top.get('name') or "")
                                    sub_inscl_name = str(subinscl_top.get('name') or "")
                                elif subinscl_top:
                                    new_type = str(subinscl_top)
                                if cardid_top:
                                    new_no = str(cardid_top)
                                hm_top = data.get('hospMain') or {}
                                if isinstance(hm_top, dict):
                                    hospmain_hcode = hm_top.get('hcode')
                                hs_top = data.get('hospSub') or {}
                                if isinstance(hs_top, dict):
                                    hospsub_hcode = hs_top.get('hcode')
                                begin_date = data.get('startDateTime')
                                expire_date = data.get('expireDateTime')
                                if ((not new_type) or (not new_no) or (not sub_inscl_name)) and isinstance(funds, list) and funds:
                                    f0 = funds[0] if isinstance(funds[0], dict) else {}
                                    if not new_type:
                                        sub = f0.get('subInscl') if isinstance(f0.get('subInscl'), dict) else None
                                        if sub:
                                            new_type = str(sub.get('id') or sub.get('name') or "")
                                            sub_inscl_name = sub_inscl_name or str(sub.get('name') or "")
                                    if not new_no:
                                        new_no = str(f0.get('cardId') or f0.get('cardID') or "")
                                    main0 = f0.get('mainInscl') if isinstance(f0.get('mainInscl'), dict) else None
                                    if main0 and not main_inscl_name:
                                        main_inscl_name = str(main0.get('name') or "")
                                    hm = f0.get('hospMain') if isinstance(f0.get('hospMain'), dict) else None
                                    if hm and not hospmain_hcode:
                                        hospmain_hcode = hm.get('hcode')
                                    hs = f0.get('hospSub') if isinstance(f0.get('hospSub'), dict) else None
                                    if hs and not hospsub_hcode:
                                        hospsub_hcode = hs.get('hcode')
                            except Exception:
                                pass
                            # persist back
                            try:
                                with db_conn.cursor() as c_upd:
                                    if self._auto_update:
                                        if self._system == 'hosxp':
                                            sql_person = (
                                                "UPDATE person SET pttype=%s, pttype_begin_date=DATE(%s), pttype_expire_date=DATE(%s), pttype_hospmain=%s, pttype_hospsub=%s, pttype_no=%s, last_update_pttype=NOW() WHERE cid=%s"
                                            )
                                            params_person = [new_type or None, begin_date or None, expire_date or None, hospmain_hcode or None, hospsub_hcode or None, new_no or None, cid]
                                            print(f"[SQL UPDATE PERSON] {sql_person}")
                                            print(f"[SQL PARAMS] {params_person}")
                                            c_upd.execute(sql_person, params_person)
                                            affected_rows = c_upd.rowcount
                                            print(f"[AFFECTED ROWS] Person table: {affected_rows} rows")
                                            
                                            sql_patient = (
                                                "UPDATE patient SET pttype=%s, pttype_no=%s, pttype_hospmain=%s, pttype_hospsub=%s, last_update=NOW() WHERE cid=%s"
                                            )
                                            params_patient = [new_type or None, new_no or None, hospmain_hcode or None, hospsub_hcode or None, cid]
                                            print(f"[SQL UPDATE PATIENT] {sql_patient}")
                                            print(f"[SQL PARAMS] {params_patient}")
                                            c_upd.execute(sql_patient, params_patient)
                                            affected_rows = c_upd.rowcount
                                            print(f"[AFFECTED ROWS] Patient table: {affected_rows} rows")
                                            
                                            sql_ovst = (
                                                "UPDATE ovst o JOIN patient p ON p.hn = o.hn SET o.pttype=%s, o.pttypeno=%s, o.hospmain=%s, o.hospsub=%s WHERE DATE(o.vstdate)=%s AND p.cid=%s"
                                            )
                                            params_ovst = [new_type or None, new_no or None, hospmain_hcode or None, hospsub_hcode or None, self._date, cid]
                                            print(f"[SQL UPDATE OVST] {sql_ovst}")
                                            print(f"[SQL PARAMS] {params_ovst}")
                                            c_upd.execute(sql_ovst, params_ovst)
                                            affected_rows = c_upd.rowcount
                                            print(f"[AFFECTED ROWS] OVST table: {affected_rows} rows")
                                        else:
                                            sets = []; params = []
                                            if new_type: sets.append("rightcode=%s"); params.append(new_type)
                                            if new_no: sets.append("rightno=%s"); params.append(new_no)
                                            if hospmain_hcode is not None: sets.append("hosmain=%s"); params.append(hospmain_hcode)
                                            if hospsub_hcode is not None: sets.append("hossub=%s"); params.append(hospsub_hcode)
                                            if begin_date: sets.append("datestart=DATE(%s)"); params.append(begin_date)
                                            if expire_date: sets.append("dateexpire=DATE(%s)"); params.append(expire_date)
                                            if sets:
                                                sets.append("dateupdate=NOW()"); params.append(cid)
                                                sql_person = "UPDATE person SET " + ", ".join(sets) + " WHERE idcard=%s"
                                                print(f"[SQL UPDATE PERSON JHCIS] {sql_person}")
                                                print(f"[SQL PARAMS] {params}")
                                                c_upd.execute(sql_person, params)
                                                affected_rows = c_upd.rowcount
                                                print(f"[AFFECTED ROWS] Person table (JHCIS): {affected_rows} rows")
                                            # selected date's visit
                                            pid_val = None
                                            c_upd.execute("SELECT pid FROM person WHERE idcard=%s LIMIT 1", (cid,))
                                            rpid = c_upd.fetchone()
                                            if rpid and len(rpid) > 0:
                                                pid_val = rpid[0]
                                            if pid_val is not None:
                                                sql_visit = (
                                                    "UPDATE visit SET rightcode=%s, rightno=%s, hosmain=%s, hossub=%s, main_inscl=%s, sub_inscl=%s, dateupdate=NOW() WHERE pid=%s AND visitdate=%s"
                                                )
                                                params_visit = [new_type or None, new_no or None, hospmain_hcode or None, hospsub_hcode or None, main_inscl_name or None, sub_inscl_name or None, pid_val, self._date]
                                                print(f"[SQL UPDATE VISIT JHCIS] {sql_visit}")
                                                print(f"[SQL PARAMS] {params_visit}")
                                                c_upd.execute(sql_visit, params_visit)
                                                affected_rows = c_upd.rowcount
                                                print(f"[AFFECTED ROWS] Visit table (JHCIS): {affected_rows} rows")
                                db_conn.commit()
                            except Exception:
                                traceback.print_exc()
                            try:
                                self.update_rights.emit(proxy_row, cid, new_type, new_no)
                            except RuntimeError:
                                pass
                            succeeded += 1
                        else:
                            failed += 1
                            continue
                finally:
                    try:
                        db_conn.close()
                    except Exception:
                        traceback.print_exc()
                    try:
                        if not self._stop:
                            self.finished_summary.emit(skipped_today, skipped_dead, succeeded, failed, token_expired)
                    except RuntimeError:
                        pass

        # Remember pending rows for resume
        self._pending_rows = list(rows)
        self._pending_debug = bool(debug)
        self._pending_force = bool(force)

        self._thread = QThread(self)
        self._worker = RightsWorker(system=system, date_str=date_str, debug=debug, force=force, auto_update=auto_update)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)

        def on_progress_row(proxy_row: int):
            idx = self.proxy.index(proxy_row, self.cid_col)
            try:
                self.table.selectRow(idx.row())
                self.table.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)
            except Exception:
                pass
            try:
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
            if token_expired:
                try:
                    self._show_status("Token หมดอายุ กำลังรีเฟรชโทเคนอัตโนมัติ...", 7000)
                except Exception:
                    pass
                if not hasattr(self, '_retry_after_refresh'):
                    self._retry_after_refresh = False
                if not self._retry_after_refresh:
                    self._retry_after_refresh = True
                    try:
                        refresh_token()
                    except Exception as ex:
                        try:
                            self._show_status(f"การขอ token ใหม่เกิดข้อผิดพลาด: {ex}", 7000)
                        except Exception:
                            pass
                        # Try to open SRM program
                        try:
                            if open_srm_program():
                                QMessageBox.warning(self, 'ล้มเหลว', f'{ex}\n\nโปรด Login ใน SRM ด้วยบัตรประชาชนของเจ้าหน้าที่ตรวจสอบสิทธิ\n\nโปรแกรม SRM ถูกเปิดขึ้นมาแล้ว')
                            else:
                                QMessageBox.warning(self, 'ล้มเหลว', f'{ex}\n\nโปรด Login ใน SRM ด้วยบัตรประชาชนของเจ้าหน้าที่ตรวจสอบสิทธิ')
                        except Exception:
                            QMessageBox.warning(self, 'ล้มเหลว', f'{ex}\n\nโปรด Login ใน SRM ด้วยบัตรประชาชนของเจ้าหน้าที่ตรวจสอบสิทธิ')
                    else:
                        QTimer.singleShot(5000, lambda: self._start_rights_worker(
                            getattr(self, '_pending_rows', []),
                            debug=getattr(self, '_pending_debug', False),
                            force=getattr(self, '_pending_force', False)
                        ))
            else:
                try:
                    self._retry_after_refresh = False
                except Exception:
                    pass
                try:
                    self._show_status('ตรวจสอบสิทธิเสร็จสิ้น', 5000)
                except Exception:
                    pass
                self._set_checking_state(False)
                # reset resume pointer on normal completion
                try:
                    self._resume_from = 0
                except Exception:
                    pass
            self._thread.quit()
            self._thread.wait()
            try:
                self._worker.deleteLater()
            except Exception:
                pass
            try:
                self._thread.deleteLater()
            except Exception:
                pass

        def on_need_resume_from(proxy_row: int):
            try:
                self._resume_from = int(proxy_row)
            except Exception:
                self._resume_from = 0

        self._worker.progress_row.connect(on_progress_row)
        self._worker.mark_checked.connect(on_mark_checked)
        self._worker.finished_summary.connect(on_finished_summary)
        self._worker.update_rights.connect(on_update_rights)
        self._worker.need_resume_from.connect(on_need_resume_from)

        self._thread.start()
        self._set_checking_state(True)
        # Stop worker on app quit
        app = QCoreApplication.instance()
        if app is not None:
            try:
                app.aboutToQuit.disconnect(self._on_about_to_quit)
            except Exception:
                pass
            app.aboutToQuit.connect(self._on_about_to_quit)

    def closeEvent(self, event):
        try:
            if hasattr(self, "_thread") and self._thread is not None and self._thread.isRunning():
                try:
                    self._thread.quit()
                except Exception:
                    pass
                try:
                    self._thread.wait(3000)
                except Exception:
                    pass
        except Exception:
            pass
        super().closeEvent(event)

    def on_table_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        col = index.column()
        # Allow context menu only on CID column
        if col != self.cid_col:
            return
        menu = QMenu(self)
        act_copy = menu.addAction("Copy CID")
        act_check = menu.addAction("ตรวจสอบสิทธิ")
        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
        if chosen is None:
            return
        try:
            if chosen == act_copy:
                val = index.data()
                if val is not None:
                    QGuiApplication.clipboard().setText(str(val))
            elif chosen == act_check:
                # Trigger rights check for the CID in this row
                try:
                    cid_val = index.data()
                except Exception as e:
                    traceback.print_exc()
                    cid_val = None
                if cid_val:
                    proxy_row = index.row()
                    self._start_rights_worker([(proxy_row, str(cid_val))], debug=True, force=True)
        except Exception:
            pass

    def on_header_context_menu(self, pos):
        header = self.table.horizontalHeader()
        logical = header.logicalIndexAt(pos)
        if logical < 0:
            return
        menu = QMenu(self)
        act_filter = menu.addAction("Filter...")
        act_clear = menu.addAction("Clear filter")
        chosen = menu.exec(header.mapToGlobal(pos))
        if chosen == act_filter:
            if logical == 0:
                return
            title = self.proxy.headerData(logical, Qt.Orientation.Horizontal)
            text, ok = QInputDialog.getText(self, "กรองข้อมูล", f"คำที่ต้องการกรองในคอลัมน์: {title}")
            if not ok:
                return
            self.proxy.setFilterKeyColumn(logical)
            if str(text).strip():
                self.proxy.setFilterRegularExpression(QRegularExpression(text))
            else:
                self.proxy.setFilterRegularExpression("")
        elif chosen == act_clear:
            self.proxy.setFilterRegularExpression("")

    def _on_about_to_quit(self):
        try:
            if hasattr(self, '_worker') and self._worker is not None and hasattr(self._worker, 'request_stop'):
                self._worker.request_stop()
        except Exception:
            pass

    def _check_and_update_rights(self, cid: str):
        """Call SRM for given CID and update rights in DB for selected date."""
        import pymysql
        cfg = self._get_db_config()
        qdate = self.date_edit.date()
        date_str = qdate.toString("yyyy-MM-dd")
        system = self._get_system()
        # Read token and call API
        try:
            token = read_token()
        except Exception as e:
            QMessageBox.warning(self, "โทเคนไม่พร้อม", str(e))
            return
        try:
            conn = pymysql.connect(**cfg)
        except Exception as e:
            QMessageBox.critical(self, "เชื่อมต่อฐานข้อมูลล้มเหลว", str(e))
            return
        try:
            ensure_srm_check_table(conn)
            resp = call_right_search(token, cid)
            if resp.status_code != 200:
                QMessageBox.warning(self, "ตรวจสิทธิไม่สำเร็จ", f"HTTP {resp.status_code}")
                return
            try:
                data = resp.json()
            except Exception:
                data = {}
            check_date = data.get('checkDate')
            funds = data.get('funds', [])
            # Extract rights
            new_type = ""
            new_no = ""
            hospmain_hcode = None
            hospsub_hcode = None
            begin_date = None
            expire_date = None
            main_inscl_name = None
            sub_inscl_name = None
            try:
                f0 = funds[0] if isinstance(funds, list) and funds and isinstance(funds[0], dict) else {}
                sub = f0.get('subInscl') if isinstance(f0.get('subInscl'), dict) else None
                if sub:
                    new_type = str(sub.get('id') or sub.get('name') or "")
                    sub_inscl_name = str(sub.get('name') or "")
                new_no = str(f0.get('cardId') or f0.get('cardID') or "")
                main0 = f0.get('mainInscl') if isinstance(f0.get('mainInscl'), dict) else None
                if main0:
                    main_inscl_name = str(main0.get('name') or "")
                hm = f0.get('hospMain') if isinstance(f0.get('hospMain'), dict) else None
                if hm:
                    hospmain_hcode = hm.get('hcode')
                hs = f0.get('hospSub') if isinstance(f0.get('hospSub'), dict) else None
                if hs:
                    hospsub_hcode = hs.get('hcode')
                begin_date = f0.get('startDateTime')
                expire_date = f0.get('expireDateTime')
            except Exception:
                pass
            # Upsert srm_check
            upsert_srm_check(conn, cid, check_date, None, funds, resp.status_code)

            with conn.cursor() as cur:
                if system == 'hosxp':
                    # Update person
                    sql_person = (
                        "UPDATE person SET "
                        "pttype=%s, pttype_begin_date=DATE(%s), pttype_expire_date=DATE(%s), "
                        "pttype_hospmain=%s, pttype_hospsub=%s, pttype_no=%s, last_update_pttype=NOW() "
                        "WHERE cid=%s"
                    )
                    cur.execute(sql_person, [
                        (new_type or None),
                        (begin_date or None),
                        (expire_date or None),
                        (hospmain_hcode or None),
                        (hospsub_hcode or None),
                        (new_no or None),
                        cid,
                    ])
                    # Update patient
                    sql_patient = (
                        "UPDATE patient SET pttype=%s, pttype_no=%s, pttype_hospmain=%s, pttype_hospsub=%s, last_update=NOW() "
                        "WHERE cid=%s"
                    )
                    cur.execute(sql_patient, [
                        (new_type or None),
                        (new_no or None),
                        (hospmain_hcode or None),
                        (hospsub_hcode or None),
                        cid,
                    ])
                    # Update today's ovst by date and cid
                    sql_ovst = (
                        "UPDATE ovst o JOIN patient p ON p.hn = o.hn "
                        "SET o.pttype=%s, o.pttypeno=%s, o.hospmain=%s, o.hospsub=%s "
                        "WHERE DATE(o.vstdate)=%s AND p.cid=%s"
                    )
                    cur.execute(sql_ovst, [
                        (new_type or None),
                        (new_no or None),
                        (hospmain_hcode or None),
                        (hospsub_hcode or None),
                        date_str,
                        cid,
                    ])
                else:
                    # JHCIS: update person
                    sets = []
                    params = []
                    if new_type:
                        sets.append("rightcode=%s"); params.append(new_type)
                    if new_no:
                        sets.append("rightno=%s"); params.append(new_no)
                    if hospmain_hcode is not None:
                        sets.append("hosmain=%s"); params.append(hospmain_hcode)
                    if hospsub_hcode is not None:
                        sets.append("hossub=%s"); params.append(hospsub_hcode)
                    if begin_date:
                        sets.append("datestart=DATE(%s)"); params.append(begin_date)
                    if expire_date:
                        sets.append("dateexpire=DATE(%s)"); params.append(expire_date)
                    if sets:
                        sets.append("dateupdate=NOW()")
                        params.append(cid)
                        cur.execute("UPDATE person SET " + ", ".join(sets) + " WHERE idcard=%s", params)
                    # Update today's visit by pid
                    pid_val = None
                    cur.execute("SELECT pid FROM person WHERE idcard=%s LIMIT 1", (cid,))
                    rpid = cur.fetchone()
                    if rpid and len(rpid) > 0:
                        pid_val = rpid[0]
                    if pid_val is not None:
                        sql_visit = (
                            "UPDATE visit SET rightcode=%s, rightno=%s, hosmain=%s, hossub=%s, "
                            "main_inscl=%s, sub_inscl=%s, dateupdate=NOW() "
                            "WHERE pid=%s AND visitdate=%s"
                        )
                        cur.execute(sql_visit, [
                            (new_type or None),
                            (new_no or None),
                            (hospmain_hcode or None),
                            (hospsub_hcode or None),
                            (main_inscl_name or None),
                            (sub_inscl_name or None),
                            pid_val,
                            date_str,
                        ])
            conn.commit()
            # Reload table to reflect any updated subinscl_name in srm_check
            try:
                self._load_for_date(qdate)
            except Exception:
                pass
            QMessageBox.information(self, "สำเร็จ", f"อัปเดตสิทธิเรียบร้อยสำหรับ CID {cid}")
        finally:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PatientToday()
    window.show()
    sys.exit(app.exec())
