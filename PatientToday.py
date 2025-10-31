import sys
import traceback
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox, QMenu
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
from PyQt6.QtCore import QDate, QLocale, Qt, QObject, QThread, pyqtSignal
from srm import (
    read_token,
    ensure_srm_check_table,
    upsert_srm_check,
    call_right_search,
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
            self.visit_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.visit_table.customContextMenuRequested.connect(self.on_table_context_menu)
            # Wire button to check selected row's CID
            self.check_rights_button.clicked.connect(self.on_check_clicked)
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
                    o.vn,
                    p.cid,
                    CONCAT_WS(' ', p.pname, p.fname, p.lname) AS fullname,
                    o.pttype,
                    sc.subinscl_name
                FROM ovst o
                JOIN patient p ON p.hn = o.hn
                LEFT JOIN srm_check sc ON sc.cid = p.cid AND DATE(sc.check_date) = %s
                WHERE DATE(o.vstdate) = %s
                ORDER BY o.vn
                """
            )
            params = (date_str, date_str)
        else:
            # JHCIS: list by visit table
            sql = (
                """
                SELECT 
                    v.visitno AS vn,
                    p.idcard AS cid,
                    CONCAT_WS(' ', t.titlename, p.fname, p.lname) AS fullname,
                    COALESCE(v.rightcode, p.rightcode) AS pttype,
                    sc.subinscl_name
                FROM visit v
                JOIN person p ON p.pid = v.pid
                LEFT JOIN ctitle t ON p.prename = t.titlecode
                LEFT JOIN srm_check sc ON sc.cid = p.idcard AND DATE(sc.check_date) = %s
                WHERE v.visitdate = %s
                ORDER BY p.idcard
                """
            )
            params = (date_str, date_str)

        rows = []
        headers = ["vn", "cid", "fullname", "pttype", "subinscl_name"]
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

    # ==== Batch processing (all rows) ====
    def _run_all_checks(self, cids: list[str]):
        class Worker(QObject):
            finished = pyqtSignal()
            error = pyqtSignal(str)
            progress = pyqtSignal(int, int)  # done, total
            def __init__(self, outer, cids):
                super().__init__()
                self.outer = outer
                self.cids = cids
            def run(self):
                import pymysql
                try:
                    token = read_token()
                except Exception as e:
                    self.error.emit(str(e))
                    return
                cfg = self.outer._get_db_config()
                done = 0
                try:
                    conn = pymysql.connect(**cfg)
                except Exception as e:
                    self.error.emit(str(e))
                    return
                try:
                    ensure_srm_check_table(conn)
                    for cid in self.cids:
                        try:
                            resp = call_right_search(token, cid)
                            try:
                                data = resp.json()
                            except Exception:
                                data = {}
                            check_date = data.get('checkDate')
                            funds = data.get('funds', [])
                            # Only upsert srm_check; UI reads subinscl_name from this table
                            upsert_srm_check(conn, cid, check_date, None, funds, resp.status_code)
                        except Exception:
                            traceback.print_exc()
                        done += 1
                        self.progress.emit(done, len(self.cids))
                finally:
                    try:
                        conn.close()
                    except Exception:
                        traceback.print_exc()
                self.finished.emit()

        try:
            self.check_rights_button.setEnabled(False)
        except Exception:
            pass
        self._thread = QThread(self)
        self._worker = Worker(self, cids)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        def _on_done():
            try:
                self._load_for_date(self.date_edit.date())
            except Exception:
                traceback.print_exc()
            try:
                self.check_rights_button.setEnabled(True)
            except Exception:
                pass
            QMessageBox.information(self, "เสร็จสิ้น", "ตรวจสอบสิทธิสำหรับผู้รับบริการทั้งหมดแล้ว")
        self._worker.finished.connect(_on_done)
        self._thread.start()

        model = QStandardItemModel()
        model.setColumnCount(len(headers))
        model.setHorizontalHeaderLabels(headers)
        for r in rows:
            items = []
            for val in r:
                text = "" if val is None else str(val)
                it = QStandardItem(text)
                it.setEditable(False)
                items.append(it)
            model.appendRow(items)

        self.visit_table.setModel(model)

    def on_table_context_menu(self, pos):
        index = self.visit_table.indexAt(pos)
        if not index.isValid():
            return
        col = index.column()
        # Allow context menu only on VN and CID columns
        if col not in (self.vn_col, self.cid_col):
            return
        menu = QMenu(self)
        act_copy = menu.addAction("Copy")
        act_check = menu.addAction("ตรวจสอบสิทธิ")
        chosen = menu.exec(self.visit_table.viewport().mapToGlobal(pos))
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
                    cid_idx = self.visit_table.model().index(index.row(), self.cid_col)
                    cid_val = cid_idx.data()
                except Exception as e:
                    traceback.print_exc()
                    cid_val = None
                if cid_val:
                    self._check_and_update_rights(str(cid_val))
        except Exception:
            pass

    def on_check_clicked(self):
        try:
            sel = self.visit_table.selectionModel()
            model = self.visit_table.model()
            if model is None:
                QMessageBox.warning(self, "ไม่พบตาราง", "ตารางข้อมูลยังไม่พร้อม")
                return
            # If a row is selected, run single check
            if sel is not None and sel.hasSelection():
                row = sel.selectedRows()[0].row()
                cid_idx = model.index(row, self.cid_col)
                cid_val = cid_idx.data() if cid_idx.isValid() else None
                if not cid_val:
                    QMessageBox.warning(self, "ไม่พบ CID", "ไม่พบค่า CID ในแถวที่เลือก")
                    return
                self._check_and_update_rights(str(cid_val))
                return
            # Otherwise, run for all rows in background
            cids = []
            try:
                rows = model.rowCount()
                for r in range(rows):
                    idx = model.index(r, self.cid_col)
                    val = idx.data() if idx.isValid() else None
                    if val:
                        cids.append(str(val))
            except Exception as e:
                traceback.print_exc()
            if not cids:
                QMessageBox.information(self, "ไม่มีข้อมูล", "ไม่พบรายการผู้รับบริการในวันที่เลือก")
                return
            self._run_all_checks(cids)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.warning(self, "ผิดพลาด", str(e))

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
