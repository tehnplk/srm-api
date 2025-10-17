import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMdiSubWindow, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Import local modules
from Main_ui import Main_ui, ConfigDialog
from mainConfig import MAIN_CONFIG

# Local imports
from Child import Child


class Main(QMainWindow, Main_ui):
    def __init__(self, hash_cid=None, parent=None):
        super().__init__(parent)
        self.hash_cid = hash_cid
        print("Main hash_cid:", self.hash_cid)
        self.setupUi(self)

        # Set window icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Connect actions
        self.actionExchange.triggered.connect(self.show_child)

        # Connect ERP menu items
        """try:
            self.actionMaterials.triggered.connect(self.show_materials)
            self.actionEquipment.triggered.connect(self.show_equipment)
        except ImportError as e:
            print(f"Warning: Could not load ERP modules: {e}")
            self.actionMaterials.setEnabled(False)
            self.actionEquipment.setEnabled(False)"""

        # Connect File menu module actions
        self.actionFileExchange.triggered.connect(self.show_child)

        # Connect View menu actions
        # Window management actions
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
            sub_window.showMaximized()  # Always maximize the window
            #self.centralwidget.tileSubWindows()  # Optional: tile windows if multiple are open

        except Exception as e:
            print(f"Error showing MDI child {title}: {e}")
            QMessageBox.critical(self, "Error", f"ไม่สามารถเปิด {title}: {str(e)}")

    def show_child(self):
        try:
            self.show_mdi_child(Child, "🏠 หน้าต่าง", None)
        except Exception as e:
            print(f"Error showing Child: {e}")
            QMessageBox.critical(self, "Error", f"ไม่สามารถเปิดหน้าต่าง: {e}")


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

    def show_config(self):
        config_dialog = ConfigDialog(self)
        config_dialog.exec()

    def show_materials(self):
        """Show materials module"""
        from ERP.Materials import Materials

        self.show_mdi_child(Materials, "วัสดุ", "")  # Using exchange icon temporarily

    def show_equipment(self):
        """Show equipment module"""
        from ERP.Equipment import Equipment

        self.show_mdi_child(Equipment, "ครุภัณฑ์", "")  # Using exchange icon temporarily

    def tile_windows(self):
        """Tile all open MDI child windows"""
        self.centralwidget.tileSubWindows()

    def cascade_windows(self):
        """Cascade all open MDI child windows"""
        self.centralwidget.cascadeSubWindows()

    def close_all_windows(self):
        """Close all open MDI child windows"""
        self.centralwidget.closeAllSubWindows()

    def change_background_color(self, bg_color="#f0f0f0", mdi_color="#d4f0ff"):
        """Change the background color of the main window"""
        self.set_background_color(self, bg_color, mdi_color)

    def set_watermark_text(
        self, text=f"Paracheck v{MAIN_CONFIG['version_name']}", color="#829C69"
    ):
        """Change the watermark text and color in the MDI area"""
        self.set_watermark(text, color)

    def set_mdi_color(self, color):
        """Set the background color of the MDI area"""
        self.set_mdi_background_color(color)

    def change_mdi_theme(self, theme_name):
        """Change the MDI area theme"""
        super().change_mdi_theme(theme_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Paracheck")
    app.setWindowIcon(QIcon("app_icon.ico"))
    window = Main()
    window.show()
    sys.exit(app.exec())
