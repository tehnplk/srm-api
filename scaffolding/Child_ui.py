import sys

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QTableView,
    QHBoxLayout,
    QPushButton,
    QApplication,
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt


class Child_ui(object):
    """
    UI class for Visit managem  ent.
    """

    def setupUi(self,Child_ui):
        """
        Set up the user interface for Visit management.
        """
        # Set window properties
        Child_ui.setWindowTitle("Visit Management")
        Child_ui.resize(1000, 700)

        # Create main layout
        self.main_layout = QVBoxLayout(Child_ui)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Create title label
        self.title_label = QLabel("Visit Management System", Child_ui)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;"
        )
        self.main_layout.addWidget(self.title_label)

        # Create button layout
        self.button_layout = QHBoxLayout()

        # Create action buttons
        self.add_button = QPushButton("Add Visit", Child_ui)
        self.add_button.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
        )
        self.button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Visit", Child_ui)
        self.edit_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        )
        self.button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Visit", Child_ui)
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """
        )
        self.button_layout.addWidget(self.delete_button)

        self.refresh_button = QPushButton("Refresh", Child_ui)
        self.refresh_button.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """
        )
        self.button_layout.addWidget(self.refresh_button)

        # Add stretch to push buttons to the left
        self.button_layout.addStretch()

        # Add button layout to main layout
        self.main_layout.addLayout(self.button_layout)

        # Create table view
        self.visit_table = QTableView(Child_ui)
        self.visit_table.setStyleSheet(
            """
            QTableView {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #3498db;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """
        )
        self.visit_table.setAlternatingRowColors(True)
        self.visit_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.visit_table.setSortingEnabled(True)

        # Add table to layout
        self.main_layout.addWidget(self.visit_table)

    def retranslateUi(self, Child_ui):
        """
        Retranslate the user interface.
        """
        Child_ui.setWindowTitle("Visit Management")
        self.title_label.setText("Visit Management System")
        self.add_button.setText("Add Visit")
        self.edit_button.setText("Edit Visit")
        self.delete_button.setText("Delete Visit")
        self.refresh_button.setText("Refresh")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    ui = Child_ui()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
