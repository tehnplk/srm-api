import sys
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QIntValidator, QGuiApplication, QKeySequence

from PersonalCheck_ui import PersonalCheck_ui
from srm import read_token, call_right_search, refresh_token


class PersonalCheck(QWidget, PersonalCheck_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Initialize CID inputs behavior
        self._init_cid_inputs()

    def on_check(self):
        try:
            QMessageBox.information(self, "ตรวจสอบสิทธิ", "ฟังก์ชันตรวจสอบสิทธิจะถูกพัฒนาในขั้นถัดไป")
        except Exception:
            pass

    def on_clear(self):
        try:
            # Clear table model
            self.result_table.setModel(None)
        except Exception:
            pass

    def on_refresh(self):
        try:
            QMessageBox.information(self, "รีเฟรช", "ทำการรีเฟรชข้อมูลแล้ว")
        except Exception:
            pass

    # ===== Logic for 13-digit CID inputs =====
    def _init_cid_inputs(self):
        try:
            validator = QIntValidator(0, 9, self)
            self._cid_count = len(getattr(self, 'cid_edits', []) or [])
            for idx, edit in enumerate(self.cid_edits):
                try:
                    edit.setValidator(validator)
                except Exception:
                    pass
                # Connect auto-advance when one digit entered
                edit.textChanged.connect(lambda _t, i=idx: self._on_digit_changed(i))
                # Install event filter for backspace behavior
                edit.installEventFilter(self)
            # Focus first edit
            if self._cid_count:
                self.cid_edits[0].setFocus()
            # Submit when pressing Return on the last edit
            if self._cid_count:
                try:
                    self.cid_edits[-1].returnPressed.connect(self._on_submit_cid)
                except Exception:
                    pass
        except Exception:
            pass

    def _on_digit_changed(self, idx: int):
        try:
            if idx < 0 or idx >= self._cid_count:
                return
            edit = self.cid_edits[idx]
            if len(edit.text()) == 1 and (idx + 1) < self._cid_count:
                nxt = self.cid_edits[idx + 1]
                nxt.setFocus()
                try:
                    nxt.selectAll()
                except Exception:
                    pass
            # Update live preview
            self._update_pid_preview()
        except Exception:
            pass

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Type.KeyPress:
                # Backspace: if current edit is empty, move to previous
                if hasattr(self, 'cid_edits') and obj in self.cid_edits:
                    # Handle Ctrl+V / Paste shortcut
                    try:
                        if event.matches(QKeySequence.StandardKey.Paste):
                            text = QGuiApplication.clipboard().text() or ""
                            digits = ''.join(ch for ch in text if ch.isdigit())
                            if digits:
                                start = self.cid_edits.index(obj)
                                for i, ch in enumerate(digits):
                                    pos = start + i
                                    if pos >= len(self.cid_edits):
                                        break
                                    self.cid_edits[pos].setText(ch)
                                next_pos = start + len(digits)
                                if next_pos < len(self.cid_edits):
                                    self.cid_edits[next_pos].setFocus()
                                    try:
                                        self.cid_edits[next_pos].selectAll()
                                    except Exception:
                                        pass
                                else:
                                    self.cid_edits[-1].setFocus()
                                self._update_pid_preview()
                                return True
                    except Exception:
                        pass
                    if event.key() == Qt.Key.Key_Backspace and obj.text() == "":
                        idx = self.cid_edits.index(obj)
                        if idx > 0:
                            prev = self.cid_edits[idx - 1]
                            prev.setFocus()
                            prev.clear()
                            try:
                                prev.selectAll()
                            except Exception:
                                pass
                            return True
                        else:
                            # Update preview even when deleting within a field
                            self._update_pid_preview()
            elif event.type() == QEvent.Type.Paste:
                # Handle paste from clipboard: fill digits across fields
                if hasattr(self, 'cid_edits') and obj in self.cid_edits:
                    try:
                        text = QGuiApplication.clipboard().text() or ""
                        digits = ''.join(ch for ch in text if ch.isdigit())
                        if not digits:
                            return False
                        start = self.cid_edits.index(obj)
                        # Fill sequentially
                        for i, ch in enumerate(digits):
                            pos = start + i
                            if pos >= len(self.cid_edits):
                                break
                            self.cid_edits[pos].setText(ch)
                        # Move focus to next empty or last field
                        next_pos = start + len(digits)
                        if next_pos < len(self.cid_edits):
                            self.cid_edits[next_pos].setFocus()
                            try:
                                self.cid_edits[next_pos].selectAll()
                            except Exception:
                                pass
                        else:
                            self.cid_edits[-1].setFocus()
                        self._update_pid_preview()
                        return True
                    except Exception:
                        return False
        except Exception:
            pass
        return super().eventFilter(obj, event)

    # Helpers
    def _set_text_if_exists(self, attr: str, text: str):
        try:
            w = getattr(self, attr, None)
            if w is not None:
                w.setText(text)
        except Exception:
            pass

    def _dash(self, value) -> str:
        try:
            text = str(value if value is not None else "").strip()
            return text if text else "-"
        except Exception:
            return "-"

    def _log(self, message: str):
        try:
            if hasattr(self, 'log_text') and self.log_text is not None:
                self.log_text.append(message)
            else:
                print(message)
        except Exception:
            print(message)

    def _fmt_code_name(self, obj: dict | None) -> str:
        try:
            obj = obj or {}
            # Support both {id,name} and {hcode,hname}
            code = str(obj.get('id') or obj.get('hcode') or '').strip()
            name = str(obj.get('name') or obj.get('hname') or '').strip()
            if code and name:
                return f"({code}) {name}"
            return name or code
        except Exception:
            return ""

    def _fmt_pid(self, pid: str) -> str:
        try:
            digits = ''.join(ch for ch in str(pid) if ch.isdigit())
            if len(digits) != 13:
                return pid
            return f"{digits[0]}-{digits[1:5]}-{digits[5:10]}-{digits[10:12]}-{digits[12]}"
        except Exception:
            return str(pid)

    def _on_submit_cid(self):
        try:
            digits = [e.text().strip() for e in getattr(self, 'cid_edits', [])]
            cid = ''.join(digits)
            self.cid = cid
            print(f"CID entered: {cid}")
            # Call rights search API
            try:
                token = read_token()
            except Exception as e:
                self._log(f"[TOKEN] ไม่พบหรืออ่านโทเค็นไม่ได้: {e}")
                QMessageBox.warning(self, "โทเคนไม่พร้อม", str(e))
                return

            resp = call_right_search(token, cid)
            self._log(f"[API] GET right-search status={resp.status_code} {getattr(resp, 'reason', '')}")
            # If unauthorized, try refresh token once
            if resp.status_code == 401:
                try:
                    self._log("[TOKEN] 401 Unauthorized -> refreshing token...")
                    token = refresh_token()
                    resp = call_right_search(token, cid)
                    self._log(f"[API] RETRY right-search status={resp.status_code} {getattr(resp, 'reason', '')}")
                except Exception as e:
                    self._log(f"[TOKEN] Refresh failed: {e}")
            if not resp.ok:
                # Populate Response tab with whatever body we have
                status_line = f"HTTP {resp.status_code} {getattr(resp, 'reason', '')}".strip()
                api_msg = None
                try:
                    js = resp.json()
                    self._log(f"[API] Error body: {js}")
                    import json as _json
                    if hasattr(self, 'raw_text') and self.raw_text is not None:
                        try:
                            self.raw_text.setPlainText(status_line + "\n\n" + _json.dumps(js, ensure_ascii=False, indent=2))
                        except Exception:
                            self.raw_text.setPlainText(status_line + "\n\n" + str(js))
                    # Try common message keys
                    api_msg = (
                        (js.get('message') if isinstance(js, dict) else None)
                        or (js.get('error_description') if isinstance(js, dict) else None)
                        or (js.get('error') if isinstance(js, dict) else None)
                    )
                except Exception:
                    self._log(f"[API] Error text: {resp.text}")
                    if hasattr(self, 'raw_text') and self.raw_text is not None:
                        self.raw_text.setPlainText(status_line + "\n\n" + (resp.text or ''))
                    api_msg = (resp.text or '').strip() or None
                # If 404, show API message in alert
                if resp.status_code == 404 and api_msg:
                    QMessageBox.warning(self, "ไม่พบข้อมูล", str(api_msg))
                else:
                    QMessageBox.warning(self, "ตรวจสอบสิทธิไม่สำเร็จ", f"HTTP {resp.status_code}")
                return

            try:
                data = resp.json() or {}
                # Pretty print JSON to Response tab with status line
                import json as _json
                if hasattr(self, 'raw_text') and self.raw_text is not None:
                    status_line = f"HTTP {resp.status_code} {getattr(resp, 'reason', '')}".strip()
                    try:
                        body = _json.dumps(data, ensure_ascii=False, indent=2)
                    except Exception:
                        body = str(data)
                    self.raw_text.setPlainText(status_line + "\n\n" + body)
            except Exception as e:
                # Non-JSON; show raw text with status line
                self._log(f"[API] Parse JSON failed: {e}")
                if hasattr(self, 'raw_text') and self.raw_text is not None:
                    status_line = f"HTTP {resp.status_code} {getattr(resp, 'reason', '')}".strip()
                    self.raw_text.setPlainText(status_line + "\n\n" + (resp.text or ''))
                QMessageBox.warning(self, "ข้อมูลไม่ถูกต้อง", str(e))
                return

            # Update UI labels if present (use '-' when missing)
            self._set_text_if_exists('value_check_date', self._dash(data.get('checkDate', '')))
            self._set_text_if_exists('value_pid', self._dash(self._fmt_pid(data.get('pid', ''))))
            self._set_text_if_exists('value_tname', self._dash(data.get('tname', '')))
            self._set_text_if_exists('value_fname', self._dash(data.get('fname', '')))
            self._set_text_if_exists('value_lname', self._dash(data.get('lname', '')))
            self._set_text_if_exists('value_nation', self._dash((data.get('nation') or {}).get('name')))
            self._set_text_if_exists('value_birth_date', self._dash(data.get('birthDate', '')))
            self._set_text_if_exists('value_sex', self._dash((data.get('sex') or {}).get('name')))

            funds = data.get('funds') or []
            f0 = funds[0] if funds else {}
            self._set_text_if_exists('value_main_inscl', self._dash(self._fmt_code_name(f0.get('mainInscl'))))
            self._set_text_if_exists('value_sub_inscl', self._dash(self._fmt_code_name(f0.get('subInscl'))))
            self._set_text_if_exists('value_hosp_main', self._dash(self._fmt_code_name(f0.get('hospMain'))))
            self._set_text_if_exists('value_hosp_sub', self._dash(self._fmt_code_name(f0.get('hospSub'))))
            self._set_text_if_exists('value_right_no', self._dash(f0.get('cardId')))

            self._log("[OK] อัปเดตผลการตรวจสอบสิทธิเรียบร้อย")
        except Exception as e:
            print(f"Error collecting CID: {e}")

    def _update_pid_preview(self):
        try:
            digits = ''.join(e.text().strip() for e in getattr(self, 'cid_edits', []))
            if hasattr(self, 'cid_preview') and self.cid_preview is not None:
                self.cid_preview.setText(self._fmt_pid(digits))
        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PersonalCheck()
    w.show()
    sys.exit(app.exec())
