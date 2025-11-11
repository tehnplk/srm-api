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
    QSizePolicy,
)
from PyQt6.QtGui import QAction, QIcon, QFont, QPainter, QPixmap, QColor, QBrush, QPalette
from PyQt6.QtCore import Qt, QSize


class Main_ui(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("HisHelp")
        MainWindow.resize(1200, 800)
        try:
            MainWindow.setStyleSheet(
                """
                /* Base window */
                QMainWindow { background-color: #f5f7fb; }
                QMdiArea { background: #f5f7fb; }

                /* Menubar */
                QMenuBar { background: #ffffff; border-bottom: 1px solid #e6e8ef; }
                QMenuBar::item { padding: 6px 10px; margin: 2px; border-radius: 6px; }
                QMenuBar::item:selected { background: #e9f2ff; }

                /* Menus */
                QMenu { background: #ffffff; border: 1px solid #e6e8ef; }
                QMenu::item { padding: 6px 12px; border-radius: 4px; }
                QMenu::item:selected { background: #e9f2ff; }

                /* Toolbar */
                QToolBar { background: #ffffff; border: 1px solid #e6e8ef; spacing: 6px; padding: 6px; }
                QToolButton { 
                    background: #f0f4ff; 
                    border: 1px solid #d6e4ff; 
                    padding: 6px 10px; 
                    border-radius: 8px; 
                }
                QToolButton:hover { background: #e6f0ff; }
                QToolButton:pressed { background: #dbe8ff; }

                /* Status bar */
                QStatusBar { background: #ffffff; border-top: 1px solid #e6e8ef; }

                /* Buttons */
                QPushButton {
                    background-color: #0d6efd;
                    color: #ffffff;
                    border: 1px solid #0b5ed7;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #0b5ed7; }
                QPushButton:pressed { background-color: #0a58ca; }
                QPushButton:disabled { background-color: #cbd5e1; color: #6b7280; border-color: #cbd5e1; }

                /* Inputs */
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background: #ffffff;
                    border: 1px solid #d9dee9;
                    border-radius: 8px;
                    padding: 6px 10px;
                }
                QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                    border: 1px solid #86b7fe;
                }

                /* Group boxes */
                QGroupBox { 
                    background-color: #ffffff; 
                    border: 1px solid #e6e8ef; 
                    border-radius: 10px; 
                    margin-top: 10px; 
                }
                QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; background: transparent; }

                /* Tabs */
                QTabWidget::pane { border: 1px solid #e6e8ef; border-radius: 8px; background: #ffffff; }
                QTabBar::tab { background: #f2f5fb; border: 1px solid #e6e8ef; padding: 8px 14px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 4px; }
                QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; }
                QTabBar::tab:hover { background: #e9f2ff; }

                /* Tables */
                QTableView { background: #ffffff; border: 1px solid #e6e8ef; gridline-color: #eef0f6; selection-background-color: #e9f2ff; selection-color: #0f172a; }
                QHeaderView::section { background: #f8fafc; border: 1px solid #e6e8ef; padding: 6px 8px; font-weight: 600; }

                /* Scrollbars (light) */
                QScrollBar:vertical { background: transparent; width: 12px; margin: 0; }
                QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 6px; min-height: 24px; }
                QScrollBar::handle:vertical:hover { background: #94a3b8; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
                QScrollBar:horizontal { background: transparent; height: 12px; margin: 0; }
                QScrollBar::handle:horizontal { background: #cbd5e1; border-radius: 6px; min-width: 24px; }
                QScrollBar::handle:horizontal:hover { background: #94a3b8; }
                """
            )
        except Exception:
            pass
        
        # Create central widget (MDI Area)
        self.centralwidget = QMdiArea()
        self.centralwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.centralwidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        MainWindow.setCentralWidget(self.centralwidget)
        # Add watermark background: "HisHelp" on the MDI area
        try:
            pix = QPixmap(420, 220)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            f = QFont("Segoe UI", 52, QFont.Weight.Bold)
            p.setFont(f)
            c = QColor(13, 110, 253)
            c.setAlpha(40 * 255 // 100)  # ~40% opacity
            p.setPen(c)
            rect = pix.rect()
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "HisHelp")
            p.end()

            brush = QBrush(pix)
            pal = self.centralwidget.palette()
            pal.setBrush(QPalette.ColorRole.Window, brush)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setPalette(pal)
        except Exception:
            pass

        # Create menu bar
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # File Menu
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")
        MainWindow.menuBar().addAction(self.menuFile.menuAction())

        # Login action
        self.actionLogin = QAction(MainWindow)
        self.actionLogin.setObjectName("actionLogin")
        self.actionLogin.setText("🔐 เข้าสู่ระบบ")
        self.actionLogin.setStatusTip("เข้าสู่ระบบ SRM API")
        self.menuFile.addAction(self.actionLogin)

        self.menuFile.addSeparator()

        # ผู้ป่วย (Patient) action
        self.actionPatient = QAction(MainWindow)
        self.actionPatient.setObjectName("actionPatient")
        self.actionPatient.setText("📋 รายชื่อทั้งหมด")
        self.actionPatient.setStatusTip("ตรวจสอบสิทธิของรายชื่อทั้งหมด")
        

        # ผู้รับบริการวันนี้ action
        self.actionPatientToday = QAction(MainWindow)
        self.actionPatientToday.setObjectName("actionPatientToday")
        self.actionPatientToday.setText("📅 ผู้รับบริการวันนี้")
        self.actionPatientToday.setStatusTip("ตรวจสอบสิทธิของผู้รับบริการวันนี้")
        
        # ตรวจสอบสิทธิ (Single) toolbar action
        self.actionEligibilitySingle = QAction(MainWindow)
        self.actionEligibilitySingle.setObjectName("actionEligibilitySingle")
        self.actionEligibilitySingle.setText("👤 ตรวจสอบสิทธิ")
        self.actionEligibilitySingle.setStatusTip("ตรวจสอบสิทธิรายบุคคล")

        # Add single eligibility action to File menu
        self.menuFile.addAction(self.actionEligibilitySingle)

        # ตรวจสอบสิทธิรายกลุ่ม (Main) menu with sub-items
        self.menuEligibility = self.menuFile.addMenu("ตรวจสอบสิทธิรายกลุ่ม")
        self.menuEligibility.setObjectName("menuEligibility")
        self.menuEligibility.setTitle("➕ ตรวจสอบสิทธิรายกลุ่ม")
        self.menuEligibility.addAction(self.actionPatient)
        self.menuEligibility.addAction(self.actionPatientToday)



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

        # ตรวจสอบเวอร์ชัน action
        self.actionCheckUpdate = QAction(MainWindow)
        self.actionCheckUpdate.setObjectName("actionCheckUpdate")
        self.actionCheckUpdate.setText("🔄 ตรวจสอบเวอร์ชัน")
        self.actionCheckUpdate.setStatusTip("ตรวจสอบอัปเดตเวอร์ชันใหม่")
        self.menuHelp.addAction(self.actionCheckUpdate)


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
        try:
            self.toolBar.setMovable(True)
            self.toolBar.setAllowedAreas(
                Qt.ToolBarArea.LeftToolBarArea
                | Qt.ToolBarArea.RightToolBarArea
                | Qt.ToolBarArea.TopToolBarArea
            )
        except Exception:
            pass
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        # Add quick single eligibility action
        self.toolBar.addAction(self.actionEligibilitySingle)

        # Expose submenu items as direct toolbar buttons
        self.toolBar.addAction(self.actionPatient)
        self.toolBar.addAction(self.actionPatientToday)


        # Keep Settings action on toolbar
        self.toolBar.addAction(self.actionSetting)

        # Add spacer to push Check Update button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolBar.addWidget(spacer)

        # Add Check Update action to toolbar (right-aligned)
        self.toolBar.addAction(self.actionCheckUpdate)

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
