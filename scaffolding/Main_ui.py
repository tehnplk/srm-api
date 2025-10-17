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
    QScrollArea,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QScrollArea,
)
from PyQt6.QtGui import QAction, QIcon, QFont
from PyQt6.QtCore import Qt
from WatermarkMdiArea import WatermarkMdiArea
from mainConfig import MAIN_CONFIG


class Main_ui(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")

        self._adjust_to_screen(MainWindow)

        self.centralwidget = WatermarkMdiArea()
        MainWindow.setCentralWidget(self.centralwidget)

        # Set application icon

        MainWindow.setWindowIcon(QIcon("app_icon.ico"))

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # Add File menu (first in order)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.menuBar().addAction(self.menuFile.menuAction())

        # Add Exchange, Query, Report to File menu
        self.actionFileExchange = QAction(MainWindow)
        self.actionFileExchange.setObjectName("actionFileExchange")
        self.menuFile.addAction(self.actionFileExchange)

        self.actionFileQuery = QAction(MainWindow)
        self.actionFileQuery.setObjectName("actionFileQuery")
        self.menuFile.addAction(self.actionFileQuery)

        self.actionFileReport = QAction(MainWindow)
        self.actionFileReport.setObjectName("actionFileReport")
        self.menuFile.addAction(self.actionFileReport)

        self.menuFile.addSeparator()

        self.actionSetting = QAction(MainWindow)
        self.actionSetting.setObjectName("actionSetting")
        self.menuFile.addAction(self.actionSetting)

        self.menuFile.addSeparator()

        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.menuFile.addAction(self.actionClose)

        # Add Claim menu (third in order)
        self.menuClaim = QMenu(self.menubar)
        self.menuClaim.setObjectName("menuClaim")
        MainWindow.menuBar().addAction(self.menuClaim.menuAction())

        # Add ERP menu (second in order)
        self.menuERP = QMenu(self.menubar)
        self.menuERP.setObjectName("menuERP")
        MainWindow.menuBar().addAction(self.menuERP.menuAction())

        # Materials action with enhanced styling
        self.actionMaterials = self.menuERP.addAction("📦 วัสดุ (Materials)")
        self.actionMaterials.setIcon(QIcon.fromTheme("folder"))

        # Equipment action with enhanced styling
        self.actionEquipment = self.menuERP.addAction("🛠️ ครุภัณฑ์ (Equipment)")
        self.actionEquipment.setIcon(QIcon.fromTheme("computer"))

        # Add View menu (fourth in order)
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.menuBar().addAction(self.menuView.menuAction())

        # Add window management actions directly to View menu
        self.actionTileWindows = QAction(MainWindow)
        self.actionTileWindows.setObjectName("actionTileWindows")
        self.menuView.addAction(self.actionTileWindows)

        self.actionCascadeWindows = QAction(MainWindow)
        self.actionCascadeWindows.setObjectName("actionCascadeWindows")
        self.menuView.addAction(self.actionCascadeWindows)

        self.actionCloseAllWindows = QAction(MainWindow)
        self.actionCloseAllWindows.setObjectName("actionCloseAllWindows")
        self.menuView.addAction(self.actionCloseAllWindows)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)  # Toolbar
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.actionExchange = QAction(MainWindow)
        self.actionExchange.setObjectName("actionExchange")

        self.actionQuery = QAction(MainWindow)
        self.actionQuery.setObjectName("actionQuery")

        self.actionReport = QAction(MainWindow)
        self.actionReport.setObjectName("actionReport")

        # Universal Healthcare Coverage
        self.actionUniversalHealth = QAction("🏥 ประกันสุขภาพ", MainWindow)
        self.actionUniversalHealth.setObjectName("actionUniversalHealth")
        self.menuClaim.addAction(self.actionUniversalHealth)

        # Social Security
        self.actionSocialSecurity = QAction("💼 ประกันสังคม", MainWindow)
        self.actionSocialSecurity.setObjectName("actionSocialSecurity")
        self.menuClaim.addAction(self.actionSocialSecurity)

        # Local Government
        self.actionLocalGov = QAction("🏛️ ท้องถิ่น", MainWindow)
        self.actionLocalGov.setObjectName("actionLocalGov")
        self.menuClaim.addAction(self.actionLocalGov)

        # Comptroller General's Department
        self.actionCGD = QAction("🏢 กรมบัญชีกลาง", MainWindow)
        self.actionCGD.setObjectName("actionCGD")
        self.menuClaim.addAction(self.actionCGD)

        # Bangkok Metropolitan Administration
        self.actionBMA = QAction("🌆 กทม", MainWindow)
        self.actionBMA.setObjectName("actionBMA")
        self.menuClaim.addAction(self.actionBMA)

        # Separator
        self.menuClaim.addSeparator()

        # iClaim
        self.actionIClaim = QAction("💳 iClaim", MainWindow)
        self.actionIClaim.setObjectName("actionIClaim")
        self.menuClaim.addAction(self.actionIClaim)

        self.actionVersion = QAction(MainWindow)
        self.actionVersion.setObjectName("actionVersion")

        # Toolbar items - new order
        self.toolBar.addAction(self.actionExchange)
        self.toolBar.addAction(self.actionQuery)
        self.toolBar.addAction(self.actionReport)
        self.toolBar.addAction(self.actionVersion)

        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            f"{MAIN_CONFIG['app_name']} v.{MAIN_CONFIG['version_name']}({MAIN_CONFIG['update_date']})"
        )

        # Retranslate menu and actions
        self.menuFile.setTitle("📄 File")
        self.actionFileExchange.setText("🧾 Exchange")
        self.actionFileQuery.setText("🤖 AI-Query")
        self.actionFileReport.setText("📊 Report")
        self.actionSetting.setText("⚙️ Setting")
        self.actionClose.setText("🚪 Close")  # Retranslate Toolbar
        self.toolBar.setWindowTitle("toolBar")
        self.actionExchange.setText("🧾 Exchange")
        self.actionQuery.setText("🤖 AI-Query")
        self.actionReport.setText("📊 Report")
        self.actionVersion.setText(f"📝 Version {MAIN_CONFIG['version_name']}")

        # Retranslate ERP menu
        self.menuERP.setTitle("📈 ERP")

        # Retranslate View menu
        self.menuView.setTitle("🗂️ View")
        self.actionTileWindows.setText("🗑️ Tile Windows")
        self.actionCascadeWindows.setText("🗑️ Cascade Windows")
        self.actionCloseAllWindows.setText("🗑️ Close All Windows")

        # Retranslate Claim menu
        self.menuClaim.setTitle("📋 Claim")

    def set_background_color(self, MainWindow, bg_color="#f0f0f0", mdi_color="#d4f0ff"):
        """Set custom background colors for the main window"""
        MainWindow.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {bg_color};
            }}
            QMdiArea {{
                background-color: {mdi_color};
                background-image: none;
            }}
            QMenuBar {{
                background-color: #ffffff;
                border-bottom: 1px solid #d0d0d0;
            }}
            QToolBar {{
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                spacing: 3px;
            }}
            QStatusBar {{
                background-color: #f8f8f8;
                border-top: 1px solid #d0d0d0;
            }}
        """
        )

    def set_watermark(self, text="PARACHECK", color=None):
        """Set watermark text and color for the MDI area"""
        if hasattr(self.centralwidget, "set_watermark"):
            self.centralwidget.set_watermark(text, color)

    def set_mdi_background_color(self, color):
        """Set the background color of the MDI area"""
        if hasattr(self.centralwidget, "set_background_color"):
            self.centralwidget.set_background_color(color)

    def change_mdi_theme(self, theme_name):
        """Change the MDI area to a predefined theme"""
        if hasattr(self.centralwidget, "change_theme"):
            self.centralwidget.change_theme(theme_name)

    def _adjust_to_screen(self, MainWindow):
        screen = QApplication.primaryScreen().availableGeometry()

        # Set width and height to 85% of screen
        new_width = int(screen.width() * 0.85)
        new_height = int(screen.height() * 0.85)

        MainWindow.resize(new_width, new_height)

        # Center the window horizontally and set top margin to 15px
        MainWindow.move((screen.width() - new_width) // 2, 15)


class ConfigDialog(QDialog):
    """Dialog to display all configuration values from mainConfig.py"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Information")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("📝 Application Configuration")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                padding: 10px;
                border-bottom: 2px solid #3498db;
                margin-bottom: 10px;
            }
        """
        )
        layout.addWidget(title_label)

        # Scroll area for config items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        config_layout.setContentsMargins(10, 10, 10, 10)
        config_layout.setSpacing(10)

        # Add config items as labels
        for key, value in MAIN_CONFIG.items():
            # Create container for each config item
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(10, 8, 10, 8)

            # Key label
            key_label = QLabel(f"{key.replace('_', ' ').title()}:")
            key_label.setMinimumWidth(120)
            key_font = QFont()
            key_font.setBold(True)
            key_label.setFont(key_font)
            key_label.setStyleSheet(
                """
                QLabel {
                    color: #34495e;
                    font-weight: bold;
                }
            """
            )

            # Value label
            value_label = QLabel(str(value))
            value_label.setWordWrap(True)
            value_label.setStyleSheet(
                """
                QLabel {
                    color: #2c3e50;
                    background-color: #ecf0f1;
                    padding: 5px 10px;
                    border-radius: 4px;
                    border: 1px solid #bdc3c7;
                }
            """
            )

            item_layout.addWidget(key_label)
            item_layout.addWidget(value_label, 1)

            # Style the item container
            item_widget.setStyleSheet(
                """
                QWidget {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    margin: 2px;
                }
                QWidget:hover {
                    border-color: #3498db;
                    background-color: #f8f9fa;
                }
            """
            )

            config_layout.addWidget(item_widget)

        # Add stretch to push items to top
        config_layout.addStretch()

        scroll_area.setWidget(config_widget)
        layout.addWidget(scroll_area)

        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.setMinimumHeight(35)
        close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                border: none;
                color: white;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        )
        close_button.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
