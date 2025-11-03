import sys
import traceback
import os
import json
import requests
from Version import NAME as APP_VERSION_NAME, RELEASE as APP_VERSION_RELEASE, CODE as APP_VERSION_CODE
from PyQt6.QtWidgets import QApplication, QMainWindow, QMdiSubWindow, QMessageBox
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QIcon

# Import local modules
from Main_ui import Main_ui
from Login import Login


class Main(QMainWindow, Main_ui):
    def __init__(self, hash_cid=None, parent=None):
        super().__init__(parent)
        self.hash_cid = hash_cid
        self.setupUi(self)

        # Set window icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "check.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        try:
            v_name = str(APP_VERSION_NAME or "").strip()
            v_rel = str(APP_VERSION_RELEASE or "").strip()
            title_extra = f" v{v_name}" if v_name else ""
            if v_rel:
                title_extra += f" ({v_rel})"
            self.setWindowTitle(f"HisHelp{title_extra}")
        except Exception as e:
            traceback.print_exc()

        # Connect actions
        self.actionLogin.triggered.connect(self.show_login)
        self.actionPatient.triggered.connect(self.show_patient)
        self.actionPatientToday.triggered.connect(self.show_patient_today)
        self.actionSetting.triggered.connect(self.show_setting)
        self.actionCheckUpdate.triggered.connect(self.show_check_update)
        self.actionAbout.triggered.connect(self.show_about)
        try:
            self.actionEligibilitySingle.triggered.connect(self.show_personal_check)
        except Exception as e:
            traceback.print_exc()
        
        
        # Connect View menu actions
        self.actionTileWindows.triggered.connect(self.tile_windows)
        self.actionCascadeWindows.triggered.connect(self.cascade_windows)
        self.actionCloseAllWindows.triggered.connect(self.close_all_windows)

    def show_mdi_child(self, child_class, title, *args, **kwargs):
        """
        Show an MDI child window with the specified class and title.

        Args:
            child_class: The class of the widget to show
            title: Window title
            *args, **kwargs: Arguments to pass to the widget's constructor
        """
        try:
            # Check if window already exists
            for window in self.centralwidget.subWindowList():
                if window.widget().__class__ == child_class:
                    window.setWindowState(
                        window.windowState() & ~Qt.WindowState.WindowMinimized
                    )
                    # Maximize existing subwindow inside MDI area
                    window.showMaximized()
                    self.centralwidget.setActiveSubWindow(window)
                    window.activateWindow()
                    return

            # Create new window
            child = child_class(*args, **kwargs)
            sub_window = self.centralwidget.addSubWindow(child)
            sub_window.setWindowTitle(title)
            # Set icon for child subwindow from window.png
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                child_icon_path = os.path.join(script_dir, "window.png")
                if os.path.exists(child_icon_path):
                    sub_window.setWindowIcon(QIcon(child_icon_path))
                else:
                    sub_window.setWindowIcon(QIcon())
            except Exception:
                pass
            sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            # Show new subwindow maximized inside MDI area
            sub_window.showMaximized()
            
            self.statusbar.showMessage(f"เปิด{title}")

        except Exception as e:
            print(f"Error showing MDI child {title}: {e}")
            QMessageBox.critical(self, "Error", f"ไม่สามารถเปิด {title}: {str(e)}")

    def show_patient(self):
        """Handle รายชื่อ/Patient menu action"""
        from Patient import Patient
        self.show_mdi_child(Patient, "📋 รายชื่อ", parent=self)

    def show_patient_today(self):
        from PatientToday import PatientToday
        self.show_mdi_child(PatientToday, "📅 ผู้รับบริการวันนี้", parent=self)

    def show_setting(self):
        """Handle ตั้งค่า menu action"""
        from Setting import Setting
        self.show_mdi_child(Setting, "⚙️ ตั้งค่า", parent=self)

    def show_login(self):
        """Handle 🔐 เข้าสู่ระบบ menu action"""
        self.show_mdi_child(Login, "🔐 เข้าสู่ระบบ", parent=self)

    def show_personal_check(self):
        """Handle 👤 ตรวจสอบสิทธิ (single) toolbar/menu action"""
        from PersonalCheck import PersonalCheck
        self.show_mdi_child(PersonalCheck, "👤 ตรวจสอบสิทธิ", parent=self)


    


    def show_check_update(self):
        """Check update from API, write new.txt if newer, and offer to download via Update.exe."""
        api_url = (
            "https://script.google.com/macros/s/AKfycbxD9CI91jGbL-MWHvBDvCqgh8s9DaTEZ38ItvX7yX37w65mQzWC_DQ5SzlrViEooh9wtg/exec"
        )
        try:
            resp = requests.get(api_url, timeout=10)
            if resp.status_code != 200:
                QMessageBox.warning(self, "อัปเดต", f"ตรวจสอบอัปเดตล้มเหลว: HTTP {resp.status_code}")
                return
            payload = resp.json()
        except Exception as e:
            QMessageBox.warning(self, "อัปเดต", f"ตรวจสอบอัปเดตล้มเหลว: {e}")
            return

        # Normalize payload: if API returns a list, use the LAST element
        if isinstance(payload, list):
            if not payload:
                data = {}
            else:
                try:
                    data = max(
                        payload,
                        key=lambda x: int(str((x or {}).get('new_version_code') or (x or {}).get('code') or -1))
                    )
                except Exception as e:
                    traceback.print_exc()
                    try:
                        data = max(payload, key=lambda x: str((x or {}).get('release') or ''))
                    except Exception as e:
                        traceback.print_exc()
                        data = payload[-1]
        else:
            data = payload if isinstance(payload, dict) else {}
        # Read new code and compare only numeric codes
        new_code = data.get('new_version_code') if 'new_version_code' in data else data.get('code')
        try:
            new_code = int(str(new_code)) if new_code is not None and str(new_code).strip() != '' else None
        except Exception as e:
            traceback.print_exc()
            new_code = None
        try:
            cur_code = int(str(APP_VERSION_CODE)) if str(APP_VERSION_CODE).strip() != '' else None
        except Exception as e:
            traceback.print_exc()
            cur_code = None

        if new_code is None or cur_code is None or not (new_code > cur_code):
            QMessageBox.information(self, "อัปเดต", "เป็นเวอร์ชันล่าสุดแล้ว")
            return

        # If newer, write new.txt (JSON) using a simple relative path
        new_path = 'new.txt'
        try:
            # augment payload with current version info
            data_out = dict(data)
            data_out['current_code'] = cur_code
            try:
                data_out['current_name'] = str(APP_VERSION_NAME)
            except Exception as e:
                traceback.print_exc()
            try:
                data_out['current_release'] = str(APP_VERSION_RELEASE)
            except Exception as e:
                traceback.print_exc()
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(data_out, f, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "อัปเดต", f"ไม่สามารถเขียนไฟล์ new.txt: {e}")
            return

        # Offer to start Update.exe to download and install (show new version details, exclude URL)
        updater_path = "Update.exe"
        if not os.path.exists(updater_path):
            QMessageBox.information(self, "อัปเดต", "ไม่พบไฟล์ Update.exe ในโฟลเดอร์โปรแกรม กรุณาตรวจสอบตัวอัปเดต")
            return

        # Build detail message
        new_name = str(data.get('new_version_name') or data.get('name') or '')
        new_code = data.get('new_version_code') if 'new_version_code' in data else data.get('code')
        rel_raw = str(data.get('release') or '')
        rel_fmt = rel_raw[:10] if 'T' in rel_raw and len(rel_raw) >= 10 else rel_raw
        notes = str(data.get('notes') or data.get('changelog') or '')
        details = []
        if new_name:
            details.append(f"เวอร์ชัน: {new_name}")
        if new_code is not None and str(new_code) != '':
            details.append(f"โค้ด: {new_code}")
        if rel_fmt:
            details.append(f"เผยแพร่: {rel_fmt}")
        if notes:
            details.append("")
            details.append(notes)
        body = "\n".join(details)

        ret = QMessageBox.question(
            self,
            "พบอัปเดต",
            (body + ("\n\n" if body else "")) + "ต้องการดาวน์โหลดและติดตั้งเดี๋ยวนี้หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ret == QMessageBox.StandardButton.Yes:
            try:
                QProcess.startDetached(updater_path, [])
                app = QApplication.instance()
                if app is not None:
                    app.quit()
            except Exception as e:
                QMessageBox.warning(self, "อัปเดต", f"ไม่สามารถเริ่ม Update.exe: {e}")

    def show_about(self):
        """Show about dialog"""
        v_name = str(APP_VERSION_NAME or "").strip()
        v_rel = str(APP_VERSION_RELEASE or "").strip()
        v_code = str(APP_VERSION_CODE or "").strip()
        ver_line = f"<p><b>เวอร์ชัน:</b> {v_name}</p>" if v_name else ""
        rel_line = f"<p><b>วันที่เผยแพร่:</b> {v_rel}</p>" if v_rel else ""
        code_line = f"<p><b>โค้ดเวอร์ชัน:</b> {v_code}</p>" if v_code else ""
        QMessageBox.about(
            self,
            "เกี่ยวกับ HisHelp",
            f"""
            <h3>HisHelp - ระบบช่วยตรวจสอบสิทธิ</h3>
            {ver_line}
            {code_line}
            {rel_line}
            <p><b>พัฒนาโดย:</b> PLK Digital Health</p>
            <p><b>คำอธิบาย:</b> เครื่องมือช่วยตรวจสอบสิทธิ์และผู้รับบริการ</p>
            <p><b>เทคโนโลยี:</b> SRM API</p>
            <hr>
            <p><i>© 2024 PLK Digital Health. All rights reserved.</i></p>
            """
        )
        self.statusbar.showMessage("แสดงข้อมูลเกี่ยวกับโปรแกรม")

    def closeEvent(self, event):
        """Handle the close event for the main window."""
        try:
            # Close all sub-windows before closing the main window
            for window in self.centralwidget.subWindowList():
                window.close()
            event.accept()
        except Exception as e:
            print(f"Error during close: {e}")
            event.accept()  # Still allow the application to close

    def tile_windows(self):
        """Tile all open MDI child windows"""
        self.centralwidget.tileSubWindows()

    def cascade_windows(self):
        """Cascade all open MDI child windows"""
        self.centralwidget.cascadeSubWindows()

    def close_all_windows(self):
        """Close all open MDI child windows"""
        self.centralwidget.closeAllSubWindows()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("HisHelp")
    try:
        if APP_VERSION_NAME:
            app.setApplicationVersion(str(APP_VERSION_NAME))
    except Exception as e:
        traceback.print_exc()
    app.setOrganizationName("SRM Team")
    # Set application icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "check.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = Main()
    window.showMaximized()
    sys.exit(app.exec())
