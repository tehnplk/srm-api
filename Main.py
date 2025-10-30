import sys
import os
import json
from Version import NAME as APP_VERSION_NAME, RELEASE as APP_VERSION_RELEASE, CODE as APP_VERSION_CODE
from PyQt6.QtWidgets import QApplication, QMainWindow, QMdiSubWindow, QMessageBox
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QIcon

# Import local modules
from Main_ui import Main_ui


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
        except Exception:
            pass

        # Connect actions
        self.actionPatient.triggered.connect(self.show_patient)
        self.actionPatientToday.triggered.connect(self.show_patient_today)
        self.actionSetting.triggered.connect(self.show_setting)
        self.actionCheckUpdate.triggered.connect(self.show_check_update)
        self.actionAbout.triggered.connect(self.show_about)
        
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

    def show_check_update(self):
        # Try to run external updater and exit
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            updater_path = os.path.join(script_dir, "Update.exe")
            if os.path.exists(updater_path):
                try:
                    QProcess.startDetached(updater_path, [])
                    app = QApplication.instance()
                    if app is not None:
                        app.quit()
                    return
                except Exception:
                    pass
        except Exception:
            pass
        # If no external updater, inform user
        QMessageBox.information(
            self,
            "อัปเดต",
            "ไม่พบไฟล์ Update.exe ในโฟลเดอร์โปรแกรม กรุณาตรวจสอบตัวอัปเดต",
        )

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
    except Exception:
        pass
    app.setOrganizationName("SRM Team")
    # Set application icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "check.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = Main()
    window.show()
    sys.exit(app.exec())
