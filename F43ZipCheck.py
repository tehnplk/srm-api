import os
import io
import csv
import zipfile
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from F43ZipCheck_ui import F43ZipCheck_ui


class F43ZipCheck(QWidget, F43ZipCheck_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Wire UI events
        self.btn_browse_zip.clicked.connect(self.on_browse_zip)
        self.btn_scan.clicked.connect(self.on_scan)
        self.btn_validate.clicked.connect(self.on_validate)
        self.btn_export.clicked.connect(self.on_export)

        # Results model
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(["file", "exists", "size_bytes", "errors"])
        self.table.setModel(self.model)

        # Define expected 43 files (basenames without extension)
        self.required_files = [
            "PERSON", "HOME", "VILLAGE", "HOUSE", "DEATH", "SERVICE", "DIAG", "DRUGALLERGY",
            "DRUGIPD", "DRUGOPD", "PROCEDURE_OPD", "PROCEDURE_IPD", "APPOINT", "ACCIDENT", "CHRONIC",
            "CHRONICFU", "DISABILITY", "DENTAL", "EPI", "FP", "LABFU", "ANC", "ANCPOST", "POSTNATAL",
            "NEWBORN", "NEWBORNCARE", "NUTRITION", "PRENATAL", "WELLCHILD", "WOMEN", "CARD",
            "SURVEILLANCE", "VMI", "VDRUG", "ICF", "SMI", "SPECIALPP", "CARE_REDUCE", "ICD10TM",
            "HEALTHSCREEN", "COMMUNITY_SERVICE", "ORALHEALTH", "REHABILITATION", "SENIOR"
        ]

        self.scan_results = []  # list of dicts per file

    def _append_row(self, file, exists, size, errors):
        items = [
            QStandardItem(str(file)),
            QStandardItem("YES" if exists else "NO"),
            QStandardItem(str(size if size is not None else "")),
            QStandardItem("; ".join(errors) if errors else ""),
        ]
        for it in items:
            it.setEditable(False)
        if not exists:
            try:
                for it in items:
                    it.setData(Qt.GlobalColor.red, role=Qt.ItemDataRole.ForegroundRole)
            except Exception:
                pass
        self.model.appendRow(items)

    def on_browse_zip(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ ZIP", "", "ZIP Files (*.zip)")
        if path:
            self.input_zip.setText(path)

    def on_scan(self):
        zip_path = self.input_zip.text().strip()
        if not zip_path or not os.path.isfile(zip_path):
            QMessageBox.warning(self, "ไฟล์ไม่ถูกต้อง", "โปรดเลือกไฟล์ ZIP ที่ถูกต้อง")
            return
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                names = zf.namelist()
                # Map basenames (upper) to ZipInfo
                by_name = {}
                for n in names:
                    base = os.path.basename(n)
                    if not base:
                        continue
                    by_name[base.upper()] = zf.getinfo(n)
                self.model.removeRows(0, self.model.rowCount())
                self.scan_results = []
                for base in self.required_files:
                    fname = f"{base}.TXT"
                    alt = f"{base}.txt"
                    zi = by_name.get(fname) or by_name.get(alt)
                    exists = zi is not None
                    size = zi.file_size if zi else None
                    errors = []
                    if not exists:
                        errors.append("ไม่พบไฟล์ใน ZIP")
                    elif size == 0:
                        errors.append("ไฟล์ว่างเปล่า")
                    self.scan_results.append({
                        'file': fname,
                        'exists': exists,
                        'size': size,
                        'errors': errors,
                    })
                    self._append_row(fname, exists, size, errors)
                self.log_label.setText("สแกน ZIP เสร็จสิ้น")
        except zipfile.BadZipFile:
            QMessageBox.warning(self, "ZIP ไม่ถูกต้อง", "ไฟล์ ZIP เสียหายหรือรูปแบบไม่ถูกต้อง")
        except Exception as e:
            QMessageBox.warning(self, "ผิดพลาด", f"ไม่สามารถอ่าน ZIP: {e}")

    def on_validate(self):
        if not self.scan_results:
            self.on_scan()
            if not self.scan_results:
                return
        missing = [r['file'] for r in self.scan_results if not r['exists']]
        empty = [r['file'] for r in self.scan_results if r['exists'] and (r['size'] or 0) == 0]
        msgs = []
        if missing:
            msgs.append(f"ขาดไฟล์ {len(missing)} รายการ")
        if empty:
            msgs.append(f"ไฟล์ว่าง {len(empty)} รายการ")
        if not msgs:
            QMessageBox.information(self, "ผลการตรวจสอบ", "ผ่านเกณฑ์เบื้องต้น")
            self.log_label.setText("ผ่านเกณฑ์เบื้องต้น")
        else:
            QMessageBox.information(self, "ผลการตรวจสอบ", "\n".join(msgs))
            self.log_label.setText("; ".join(msgs))

    def on_export(self):
        if not self.scan_results:
            QMessageBox.information(self, "ไม่มีข้อมูล", "โปรดสแกนก่อนส่งออก")
            return
        out_path, _ = QFileDialog.getSaveFileName(self, "บันทึกผลลัพธ์", "f43zipcheck.csv", "CSV Files (*.csv)")
        if not out_path:
            return
        try:
            with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(["file", "exists", "size_bytes", "errors"])
                for r in self.scan_results:
                    w.writerow([
                        r['file'],
                        "YES" if r['exists'] else "NO",
                        r['size'] if r['size'] is not None else "",
                        ", ".join(r['errors']) if r['errors'] else "",
                    ])
            QMessageBox.information(self, "สำเร็จ", "บันทึกไฟล์เรียบร้อย")
        except Exception as e:
            QMessageBox.warning(self, "ล้มเหลว", f"ไม่สามารถบันทึกไฟล์: {e}")
