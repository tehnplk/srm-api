import sys

from PyQt6.QtWidgets import QWidget,QDialog, QMessageBox, QApplication

from Child_ui import Child_ui

class Child(QDialog, Child_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        # Connect button signals
        self.add_button.clicked.connect(self.add_visit)
        self.edit_button.clicked.connect(self.edit_visit)
        self.delete_button.clicked.connect(self.delete_visit)
        self.refresh_button.clicked.connect(self.refresh_data)
    
    def add_visit(self):
        """
        Handle add visit button click.
        """
        QMessageBox.information(self, "Add Visit", "Add Visit functionality will be implemented here.")
    
    def edit_visit(self):
        """
        Handle edit visit button click.
        """
     
        QMessageBox.information(self, "Edit Visit", "Edit Visit functionality will be implemented here.")
    
    def delete_visit(self):
        """
        Handle delete visit button click.
        """
      
        reply = QMessageBox.question(self, "Delete Visit", 
                                   "Are you sure you want to delete the selected visit?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
    
    def refresh_data(self):
        """
        Handle refresh button click.
        """
       
        QMessageBox.information(self, "Refresh", "Data refreshed successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Child()
    window.show()
    sys.exit(app.exec())
