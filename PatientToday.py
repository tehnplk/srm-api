import sys
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox, QMenu
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
from PyQt6.QtCore import QDate, QLocale, Qt

from PatientToday_ui import PatientToday_ui


class PatientToday(QWidget, PatientToday_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Initialize date picker to today and wire change handler
        try:
            self.date_edit.setDate(QDate.currentDate())
        except Exception:
            pass
        # Force Gregorian year and Western digits (avoid Thai/Buddhist year and numerals)
        try:
            en_us = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
            self.date_edit.setLocale(en_us)
            cw = self.date_edit.calendarWidget()
            if cw is not None:
                cw.setLocale(en_us)
        except Exception:
            pass
        try:
            self.date_edit.dateChanged.connect(self.on_date_changed)
        except Exception:
            pass

        # Initial load
        try:
            self._load_for_date(self.date_edit.date())
        except Exception:
            pass

        # Setup context menu for copying vn/cid (set up once)
        try:
            self.vn_col = 0
            self.cid_col = 1
            self.visit_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.visit_table.customContextMenuRequested.connect(self.on_table_context_menu)
        except Exception:
            pass

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

    def _load_for_date(self, qdate: QDate):
        import pymysql
        cfg = self._get_db_config()
        if not str(cfg.get("host", "")).strip() or not str(cfg.get("user", "")).strip() or not str(cfg.get("database", "")).strip():
            raise ValueError("โปรดตั้งค่าการเชื่อมต่อฐานข้อมูลให้ครบถ้วนในเมนู ตั้งค่า")

        date_str = qdate.toString("yyyy-MM-dd")

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

        rows = []
        headers = ["vn", "cid", "fullname", "pttype", "subinscl_name"]
        conn = pymysql.connect(**cfg)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (date_str, date_str))
                rows = cur.fetchall() or []
        finally:
            try:
                conn.close()
            except Exception:
                pass

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
        chosen = menu.exec(self.visit_table.viewport().mapToGlobal(pos))
        if chosen is None:
            return
        try:
            val = index.data()
            if val is not None:
                QGuiApplication.clipboard().setText(str(val))
        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PatientToday()
    window.show()
    sys.exit(app.exec())
