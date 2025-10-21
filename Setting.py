import sys
from typing import Dict

from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox, QMdiSubWindow
from PyQt6.QtCore import QSettings, QLocale

from Setting_ui import Setting_ui


class Setting(QWidget, Setting_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Ensure Western numerals in spin boxes regardless of OS locale
        en_locale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
        self.port_spin.setLocale(en_locale)
        self.timeout_spin.setLocale(en_locale)

        # QSettings for persistence
        self.settings = QSettings("SRM_API", "MySQL_Settings")

        # Wire buttons
        self.test_button.clicked.connect(self.test_connection)
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.on_cancel)

        # Settings are loaded during UI setup via QSettings

    def get_config(self) -> Dict:
        return {
            "host": self.host_edit.text().strip(),
            "port": int(self.port_spin.value()),
            "database": self.database_edit.text().strip(),
            "user": self.username_edit.text().strip(),
            "password": self.password_edit.text(),
            "connect_timeout": int(self.timeout_spin.value()),
            "charset": "utf8mb4",
            "system": self.system_combo.currentText(),
        }

    def validate_required(self) -> bool:
        missing = []
        if not self.host_edit.text().strip():
            missing.append("Host")
        if not self.database_edit.text().strip():
            missing.append("Database")
        if not self.username_edit.text().strip():
            missing.append("Username")
        if missing:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", f"กรุณากรอก: {', '.join(missing)}")
            return False
        return True

    def test_connection(self):
        if not self.validate_required():
            return
        try:
            import pymysql

            cfg = self.get_config()
            conn = pymysql.connect(
                host=cfg["host"],
                port=cfg["port"],
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                charset=cfg["charset"],
                connect_timeout=cfg["connect_timeout"],
            )
            with conn.cursor() as cur:
                cur.execute("SELECT VERSION()")
                version = cur.fetchone()
            conn.close()
            QMessageBox.information(self, "สำเร็จ", f"เชื่อมต่อสำเร็จ\nMySQL: {version[0]}")
        except ModuleNotFoundError:
            QMessageBox.critical(self, "ไม่พบไลบรารี", "ไม่พบ PyMySQL\nโปรดติดตั้งด้วย: pip install PyMySQL")
        except Exception as e:
            QMessageBox.critical(self, "การเชื่อมต่อล้มเหลว", str(e))

    def save_settings(self):
        if not self.validate_required():
            return
        try:
            cfg = self.get_config()
            self.settings.setValue("host", cfg["host"])
            self.settings.setValue("port", cfg["port"])
            self.settings.setValue("database", cfg["database"])
            self.settings.setValue("user", cfg["user"])
            self.settings.setValue("password", cfg["password"])
            self.settings.setValue("timeout", cfg["connect_timeout"])
            self.settings.setValue("system", cfg["system"])
            self.settings.sync()
            QMessageBox.information(self, "บันทึกแล้ว", "บันทึกการตั้งค่าเรียบร้อย")
            # Close settings form after successful save
            self.on_cancel()
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"บันทึกล้มเหลว: {e}")

    def load_settings(self):
        try:
            host = self.settings.value("host", "localhost")
            port = int(self.settings.value("port", 3306))
            database = self.settings.value("database", "")
            user = self.settings.value("user", "")
            password = self.settings.value("password", "")
            timeout = int(self.settings.value("timeout", 10))
            system = self.settings.value("system", "jhcis")

            self.host_edit.setText(host)
            self.port_spin.setValue(port)
            self.database_edit.setText(database)
            self.username_edit.setText(user)
            self.password_edit.setText(password)
            self.timeout_spin.setValue(timeout)
            # set current system selection safely
            idx = self.system_combo.findText(system)
            if idx >= 0:
                self.system_combo.setCurrentIndex(idx)
            else:
                self.system_combo.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"โหลดการตั้งค่าล้มเหลว: {e}")

    def on_cancel(self):
        """Close the Settings window, ensuring MDI subwindow wrapper is closed."""
        try:
            # Find the QMdiSubWindow ancestor and close it only
            w = self
            while w is not None and not isinstance(w, QMdiSubWindow):
                w = w.parent()
            if isinstance(w, QMdiSubWindow):
                w.close()
            else:
                # Not in MDI: just close this widget
                self.close()
        except Exception:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Setting()
    window.show()
    sys.exit(app.exec())
