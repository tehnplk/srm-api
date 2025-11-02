import sys
import os
import csv
import traceback
import pandas as pd
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QWidget, QDialog, QMessageBox, QFileDialog, QApplication
from PyQt6.QtCore import QThread, pyqtSignal, Qt

from Export16Files_ui import Export16Files_ui


class ExportWorker(QThread):
    """
    Worker thread for exporting files to prevent UI freezing.
    """
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    log_message = pyqtSignal(str)
    export_completed = pyqtSignal(bool, str)
    file_exported = pyqtSignal(str, bool, str)

    def __init__(self, export_settings, selected_files, export_path, file_format):
        super().__init__()
        self.export_settings = export_settings
        self.selected_files = selected_files
        self.export_path = export_path
        self.file_format = file_format
        self.is_running = True

    def run(self):
        """
        Main export process running in separate thread.
        """
        try:
            self.status_updated.emit("กำลังเริ่มการส่งออกข้อมูล...")
            self.log_message.emit(f"เริ่มต้นการส่งออกข้อมูล: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.log_message.emit(f"ที่เก็บไฟล์: {self.export_path}")
            self.log_message.emit(f"รูปแบบไฟล์: {self.file_format}")

            total_files = len(self.selected_files)
            exported_count = 0

            for i, file_info in enumerate(self.selected_files, 1):
                if not self.is_running:
                    self.status_updated.emit("การส่งออกถูกยกเลิก")
                    self.log_message.emit("การส่งออกถูกยกเลิกโดยผู้ใช้")
                    self.export_completed.emit(False, "การส่งออกถูกยกเลิก")
                    return

                file_name, file_type = file_info
                self.status_updated.emit(f"กำลังส่งออก: {file_name}")
                self.log_message.emit(f"กำลังประมวลผล: {file_name}")

                try:
                    # Simulate file export process
                    success = self.export_file(file_name, file_type, i)
                    
                    if success:
                        exported_count += 1
                        self.file_exported.emit(file_name, True, "ส่งออกสำเร็จ")
                        self.log_message.emit(f"✓ {file_name} - ส่งออกสำเร็จ")
                    else:
                        self.file_exported.emit(file_name, False, "ส่งออกล้มเหลว")
                        self.log_message.emit(f"✗ {file_name} - ส่งออกล้มเหลว")

                except Exception as e:
                    self.file_exported.emit(file_name, False, f"ข้อผิดพลาด: {str(e)}")
                    self.log_message.emit(f"✗ {file_name} - ข้อผิดพลาด: {str(e)}")
                    print(f"Error exporting {file_name}: {e}")
                    traceback.print_exc()

                # Update progress
                progress = int((i / total_files) * 100)
                self.progress_updated.emit(progress)

            # Final summary
            self.status_updated.emit(f"ส่งออกข้อมูลเสร็จสิ้น: {exported_count}/{total_files} แฟ้ม")
            self.log_message.emit(f"สรุป: ส่งออกสำเร็จ {exported_count}/{total_files} แฟ้ม")
            self.log_message.emit(f"เสร็จสิ้น: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if exported_count == total_files:
                self.export_completed.emit(True, f"ส่งออกข้อมูลสำเร็จทั้งหมด {total_files} แฟ้ม")
            else:
                self.export_completed.emit(False, f"ส่งออกข้อมูลสำเร็จ {exported_count}/{total_files} แฟ้ม")

        except Exception as e:
            error_msg = f"เกิดข้อผิดพลาดในการส่งออก: {str(e)}"
            self.status_updated.emit(error_msg)
            self.log_message.emit(f"ข้อผิดพลาดร้ายแรง: {error_msg}")
            self.export_completed.emit(False, error_msg)
            print(f"Export error: {e}")
            traceback.print_exc()

    def export_file(self, file_name, file_type, file_index):
        """
        Export individual file based on type and format.
        """
        try:
            # Generate sample data for demonstration
            # In real implementation, this would query database or other data sources
            sample_data = self.generate_sample_data(file_type)
            
            if not sample_data:
                return False

            # Create filename based on format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = self.safe_filename(file_name)
            
            if self.file_format == "CSV":
                filename = f"{safe_filename}_{timestamp}.csv"
                filepath = os.path.join(self.export_path, filename)
                return self.export_to_csv(filepath, sample_data)
            
            elif self.file_format == "Excel (.xlsx)":
                filename = f"{safe_filename}_{timestamp}.xlsx"
                filepath = os.path.join(self.export_path, filename)
                return self.export_to_excel(filepath, sample_data)
            
            elif self.file_format == "Text (.txt)":
                filename = f"{safe_filename}_{timestamp}.txt"
                filepath = os.path.join(self.export_path, filename)
                return self.export_to_text(filepath, sample_data)
            
            return False

        except Exception as e:
            print(f"Error in export_file: {e}")
            return False

    def generate_sample_data(self, file_type):
        """
        Generate sample data for different file types.
        In real implementation, this would be replaced with actual data queries.
        """
        try:
            if file_type == "patient":
                return [
                    {"HN": "123456", "ชื่อ": "สมชาย ใจดี", "อายุ": "45", "เพศ": "ชาย", "ที่อยู่": "กรุงเทพฯ"},
                    {"HN": "123457", "ชื่อ": "สมหญิง รักดี", "อายุ": "32", "เพศ": "หญิง", "ที่อยู่": "นนทบุรี"}
                ]
            elif file_type == "admission":
                return [
                    {"AN": "600001", "HN": "123456", "วันที่รับ": "2024-01-15", "วันที่จำหน่าย": "2024-01-17", "แผนก": "อายุรกรรม"},
                    {"AN": "600002", "HN": "123457", "วันที่รับ": "2024-01-16", "วันที่จำหน่าย": "2024-01-18", "แผนก": "สูติกรรม"}
                ]
            elif file_type == "diagnosis":
                return [
                    {"AN": "600001", "รหัสโรค": "I10", "ชื่อโรค": "ความดันโลหิตสูง", "ประเภท": "หลัก"},
                    {"AN": "600002", "รหัสโรค": "O80", "ชื่อโรค": "คลอดปกติ", "ประเภท": "หลัก"}
                ]
            else:
                # Generic data for other file types
                return [
                    {"ID": "001", "รายการ": "ตัวอย่างข้อมูล", "จำนวน": "100", "ราคา": "500.00"},
                    {"ID": "002", "รายการ": "ข้อมูลทดสอบ", "จำนวน": "50", "ราคา": "250.00"}
                ]
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []

    def export_to_csv(self, filepath, data):
        """
        Export data to CSV format.
        """
        try:
            if not data:
                return False
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def export_to_excel(self, filepath, data):
        """
        Export data to Excel format.
        """
        try:
            if not data:
                return False
            
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False

    def export_to_text(self, filepath, data):
        """
        Export data to text format.
        """
        try:
            if not data:
                return False
            
            with open(filepath, 'w', encoding='utf-8') as txtfile:
                txtfile.write("=" * 50 + "\n")
                txtfile.write(f"ส่งออกข้อมูล: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                txtfile.write("=" * 50 + "\n\n")
                
                for row in data:
                    for key, value in row.items():
                        txtfile.write(f"{key}: {value}\n")
                    txtfile.write("-" * 30 + "\n")
            return True
        except Exception as e:
            print(f"Error exporting to text: {e}")
            return False

    def safe_filename(self, filename):
        """
        Convert filename to safe format for file system.
        """
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        safe_name = filename
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Remove Thai characters that might cause issues
        safe_name = ''.join(c for c in safe_name if ord(c) < 256 or c in ' ')
        
        # Replace spaces with underscores and limit length
        safe_name = safe_name.replace(' ', '_')[:50]
        
        return safe_name.strip('_')

    def stop(self):
        """
        Stop the export process.
        """
        self.is_running = False


class Export16Files(QDialog, Export16Files_ui):
    """
    Main dialog for exporting 16 files module.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.export_worker = None
        
        # Connect signals
        self.connect_signals()
        
        # Initialize UI state
        self.initialize_ui()

    def connect_signals(self):
        """
        Connect UI signals to their handlers.
        """
        # Button connections
        self.browse_button.clicked.connect(self.browse_export_path)
        self.export_button.clicked.connect(self.start_export)
        self.cancel_button.clicked.connect(self.cancel_export)
        
        # Checkbox connections
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        
        # Date range connections
        self.start_date.dateChanged.connect(self.validate_dates)
        self.end_date.dateChanged.connect(self.validate_dates)

    def initialize_ui(self):
        """
        Initialize UI to default state.
        """
        self.export_button.setEnabled(True)
        self.cancel_button.setText("ปิด")
        self.progress_bar.setVisible(False)
        self.status_label.setText("พร้อมส่งออกข้อมูล")
        self.log_text.clear()

    def browse_export_path(self):
        """
        Open folder browser to select export path.
        """
        try:
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "เลือกโฟลเดอร์สำหรับเก็บไฟล์",
                self.export_path_edit.text(),
                QFileDialog.Option.ShowDirsOnly
            )
            
            if folder_path:
                self.export_path_edit.setText(folder_path)
                self.log_message(f"เลือกโฟลเดอร์: {folder_path}")
        except Exception as e:
            print(f"Error browsing folder: {e}")
            traceback.print_exc()

    def toggle_select_all(self, state):
        """
        Toggle all file checkboxes based on select all checkbox.
        """
        try:
            checked = state == Qt.CheckState.Checked.value
            for checkbox in self.file_checkboxes:
                checkbox.setChecked(checked)
        except Exception as e:
            print(f"Error toggling select all: {e}")
            traceback.print_exc()

    def validate_dates(self):
        """
        Validate date range selection.
        """
        try:
            start_date = self.start_date.date().toPython()
            end_date = self.end_date.date().toPython()
            
            if start_date > end_date:
                self.end_date.setDate(self.start_date.date())
                self.log_message("วันที่สิ้นสุดต้องไม่น้อยกว่าวันที่เริ่มต้น")
        except Exception as e:
            print(f"Error validating dates: {e}")
            traceback.print_exc()

    def get_selected_files(self):
        """
        Get list of selected files for export.
        """
        selected_files = []
        file_types = [
            ("แฟ้มข้อมูลผู้ป่วย (Patient)", "patient"),
            ("แฟ้มการรับบริการ (Admission)", "admission"),
            ("แฟ้มการวินิจฉัย (Diagnosis)", "diagnosis"),
            ("แฟ้มการผ่าตัด (Surgery)", "surgery"),
            ("แฟ้มยาและเวชภัณฑ์ (Medication)", "medication"),
            ("แฟ้มบริการพยาธิวิทยา (Pathology)", "pathology"),
            ("แฟ้มบริการรังสีวิทยา (Radiology)", "radiology"),
            ("แฟ้มการจำหน่าย (Discharge)", "discharge"),
            ("แฟ้มแพทย์ (Doctor)", "doctor"),
            ("แฟ้มพยาบาล (Nurse)", "nurse"),
            ("แฟ้มห้องยา (Pharmacy)", "pharmacy"),
            ("แฟ้มห้องปฏิบัติการ (Laboratory)", "laboratory"),
            ("แฟ้มค่าใช้จ่าย (Charges)", "charges"),
            ("แฟ้มการเยี่ยมไข้ (Visit)", "visit"),
            ("แฟ้มการส่งต่อ (Referral)", "referral"),
            ("แฟ้มสรุปรายวัน (Daily Summary)", "daily_summary")
        ]
        
        for i, checkbox in enumerate(self.file_checkboxes):
            if checkbox.isChecked():
                selected_files.append(file_types[i])
        
        return selected_files

    def start_export(self):
        """
        Start the export process.
        """
        try:
            # Validate inputs
            selected_files = self.get_selected_files()
            if not selected_files:
                QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกอย่างน้อย 1 แฟ้มที่ต้องการส่งออก")
                return
            
            export_path = self.export_path_edit.text()
            if not os.path.exists(export_path):
                QMessageBox.warning(self, "คำเตือน", "โฟลเดอร์ที่เลือกไม่มีอยู่จริง")
                return
            
            # Prepare export settings
            export_settings = {
                'start_date': self.start_date.date().toPython(),
                'end_date': self.end_date.date().toPython(),
                'export_path': export_path,
                'file_format': self.format_combo.currentText()
            }
            
            # Update UI for export
            self.export_button.setEnabled(False)
            self.cancel_button.setText("ยกเลิก")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.log_text.clear()
            
            # Create and start worker thread
            self.export_worker = ExportWorker(
                export_settings,
                selected_files,
                export_path,
                self.format_combo.currentText()
            )
            
            # Connect worker signals
            self.export_worker.progress_updated.connect(self.progress_bar.setValue)
            self.export_worker.status_updated.connect(self.status_label.setText)
            self.export_worker.log_message.connect(self.log_message)
            self.export_worker.export_completed.connect(self.export_finished)
            self.export_worker.file_exported.connect(self.file_export_finished)
            
            # Start export
            self.export_worker.start()
            
        except Exception as e:
            print(f"Error starting export: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถเริ่มการส่งออกได้: {str(e)}")

    def cancel_export(self):
        """
        Cancel export process or close dialog.
        """
        try:
            if self.export_worker and self.export_worker.isRunning():
                # Stop the worker thread
                self.export_worker.stop()
                self.export_worker.wait()
                self.initialize_ui()
            else:
                # Close dialog
                self.close()
        except Exception as e:
            print(f"Error canceling export: {e}")
            traceback.print_exc()

    def export_finished(self, success, message):
        """
        Handle export completion.
        """
        try:
            self.initialize_ui()
            
            if success:
                QMessageBox.information(self, "สำเร็จ", message)
            else:
                QMessageBox.warning(self, "เตือน", message)
                
            # Open export folder if successful
            if success:
                try:
                    os.startfile(self.export_path_edit.text())
                except:
                    pass
                    
        except Exception as e:
            print(f"Error in export finished: {e}")
            traceback.print_exc()

    def file_export_finished(self, filename, success, message):
        """
        Handle individual file export completion.
        """
        # This can be used for individual file status updates
        pass

    def log_message(self, message):
        """
        Add message to log text area.
        """
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] {message}")
        except Exception as e:
            print(f"Error logging message: {e}")

    def closeEvent(self, event):
        """
        Handle dialog close event.
        """
        try:
            if self.export_worker and self.export_worker.isRunning():
                reply = QMessageBox.question(
                    self,
                    "ยืนยันการปิด",
                    "การส่งออกข้อมูลยังดำเนินการอยู่ ต้องการยกเลิกและปิดหรือไม่?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.export_worker.stop()
                    self.export_worker.wait()
                    event.accept()
                else:
                    event.ignore()
            else:
                event.accept()
        except Exception as e:
            print(f"Error in close event: {e}")
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Export16Files()
    window.show()
    sys.exit(app.exec())
