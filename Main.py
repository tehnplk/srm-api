import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMdiSubWindow, QMessageBox
from PyQt6.QtCore import Qt
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
        icon_path = os.path.join(script_dir, "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Connect actions
        self.actionPatient.triggered.connect(self.show_patient)
        self.actionSetting.triggered.connect(self.show_setting)
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
                    self.centralwidget.setActiveSubWindow(window)
                    window.activateWindow()
                    return

            # Create new window
            child = child_class(*args, **kwargs)
            sub_window = self.centralwidget.addSubWindow(child)
            sub_window.setWindowTitle(title)
            sub_window.resize(800, 600)
            sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            sub_window.show()
            
            self.statusbar.showMessage(f"เปิด{title}")

        except Exception as e:
            print(f"Error showing MDI child {title}: {e}")
            QMessageBox.critical(self, "Error", f"ไม่สามารถเปิด {title}: {str(e)}")

    def show_patient(self):
        """Handle รายชื่อ/Patient menu action"""
        from Patient import Patient
        self.show_mdi_child(Patient, "📋 รายชื่อ", parent=self)

    def show_setting(self):
        """Handle ตั้งค่า menu action"""
        from Setting import Setting
        self.show_mdi_child(Setting, "⚙️ ตั้งค่า", parent=self)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "เกี่ยวกับโปรแกรม",
            """
            <h3>SRM API - ระบบจัดการข้อมูล</h3>
            <p><b>เวอร์ชัน:</b> 1.0.0</p>
            <p><b>พัฒนาโดย:</b> SRM Team</p>
            <p><b>คำอธิบาย:</b> ระบบจัดการข้อมูลรายชื่อ</p>
            <p><b>เทคโนโลยี:</b> Python 3.12 + PyQt6</p>
            <hr>
            <p><i>© 2024 SRM API. All rights reserved.</i></p>
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
    app.setApplicationName("SRM API")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SRM Team")
    
    window = Main()
    window.show()
    sys.exit(app.exec())
