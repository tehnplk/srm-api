from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QMdiArea,
    QApplication,
    QMenu,
    QToolBar,
    QToolButton,
    QDialog,
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)
from PyQt6.QtGui import QAction, QIcon, QFont
from PyQt6.QtCore import Qt, QSize


class Main_ui(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("ตรวจสอบสิทธิด้วย SRM")
        MainWindow.resize(1200, 800)
        
        # Create central widget (MDI Area)
        self.centralwidget = QMdiArea()
        self.centralwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.centralwidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        MainWindow.setCentralWidget(self.centralwidget)

        # Create menu bar
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # File Menu
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")
        MainWindow.menuBar().addAction(self.menuFile.menuAction())

        # ผู้ป่วย (Patient) action
        self.actionPatient = QAction(MainWindow)
        self.actionPatient.setObjectName("actionPatient")
        self.actionPatient.setText("📋 รายชื่อ")
        self.actionPatient.setStatusTip("จัดการรายชื่อ")
        self.menuFile.addAction(self.actionPatient)

        # Separator
        self.menuFile.addSeparator()

        # ตั้งค่า action
        self.actionSetting = QAction(MainWindow)
        self.actionSetting.setObjectName("actionSetting")
        self.actionSetting.setText("⚙️ ตั้งค่า")
        self.actionSetting.setStatusTip("ตั้งค่าระบบ")
        self.menuFile.addAction(self.actionSetting)

        # View Menu
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuView.setTitle("View")
        MainWindow.menuBar().addAction(self.menuView.menuAction())

        # Add window management actions to View menu
        self.actionTileWindows = QAction(MainWindow)
        self.actionTileWindows.setObjectName("actionTileWindows")
        self.actionTileWindows.setText("🔲 Tile Windows")
        self.actionTileWindows.setStatusTip("จัดเรียงหน้าต่างแบบกระเบื้อง")
        self.menuView.addAction(self.actionTileWindows)

        self.actionCascadeWindows = QAction(MainWindow)
        self.actionCascadeWindows.setObjectName("actionCascadeWindows")
        self.actionCascadeWindows.setText("📋 Cascade Windows")
        self.actionCascadeWindows.setStatusTip("จัดเรียงหน้าต่างแบบซ้อนทับ")
        self.menuView.addAction(self.actionCascadeWindows)

        self.actionCloseAllWindows = QAction(MainWindow)
        self.actionCloseAllWindows.setObjectName("actionCloseAllWindows")
        self.actionCloseAllWindows.setText("❌ Close All Windows")
        self.actionCloseAllWindows.setStatusTip("ปิดหน้าต่างทั้งหมด")
        self.menuView.addAction(self.actionCloseAllWindows)

        # Help Menu
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuHelp.setTitle("Help")
        MainWindow.menuBar().addAction(self.menuHelp.menuAction())

        # เกี่ยวกับ action
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout.setText("ℹ️ เกี่ยวกับ")
        self.actionAbout.setStatusTip("เกี่ยวกับโปรแกรม")
        self.menuHelp.addAction(self.actionAbout)

        # Create toolbar
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toolBar.setIconSize(QSize(32, 32))
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        # Add ผู้ป่วย button to toolbar
        self.toolBar.addAction(self.actionPatient)
        # Add ตั้งค่า button to toolbar
        self.toolBar.addAction(self.actionSetting)

        # Create status bar
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.showMessage("พร้อมใช้งาน")



if __name__ == "__main__":
    app = QApplication([])
    window = QMainWindow()
    ui = Main_ui()
    ui.setupUi(window)
    window.show()
    app.exec()
