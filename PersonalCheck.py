import sys
import traceback
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QIntValidator, QGuiApplication, QKeySequence

from PersonalCheck_ui import PersonalCheck_ui
from srm import read_token, call_right_search, refresh_token
from QtSmartCard import SmartCardObserver

class PersonalCheck(QWidget, PersonalCheck_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Initialize CID inputs behavior
        self._init_cid_inputs()
        self.smc = SmartCardObserver(read_photo=True)
        self.smc.signal_data.connect(self.smc_data)
        self.smc.signal_photo.connect(self.smc_photo)
        self.smc.signal_state.connect(self.smc_state)

    def on_check(self):
        try:
            QMessageBox.information(self, "ตรวจสอบสิทธิ", "ฟังก์ชันตรวจสอบสิทธิจะถูกพัฒนาในขั้นถัดไป")
        except Exception as e:
            traceback.print_exc()

    def on_clear(self):
        try:
            # Clear table model
            self.result_table.setModel(None)
        except Exception as e:
            traceback.print_exc()

    def on_refresh(self):
        try:
            QMessageBox.information(self, "รีเฟรช", "ทำการรีเฟรชข้อมูลแล้ว")
        except Exception as e:
            traceback.print_exc()

    # ===== Logic for 13-digit CID inputs =====
    def _init_cid_inputs(self):
        try:
            validator = QIntValidator(0, 9, self)
            self._cid_count = len(getattr(self, 'cid_edits', []) or [])
            for idx, edit in enumerate(self.cid_edits):
                try:
                    edit.setValidator(validator)
                except Exception as e:
                    traceback.print_exc()
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
                except Exception as e:
                    traceback.print_exc()
        except Exception as e:
            traceback.print_exc()

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
                except Exception as e:
                    traceback.print_exc()
            # Update live preview
            self._update_pid_preview()
        except Exception as e:
            traceback.print_exc()

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
                                    except Exception as e:
                                        traceback.print_exc()
                                else:
                                    self.cid_edits[-1].setFocus()
                                self._update_pid_preview()
                                return True
                    except Exception as e:
                        traceback.print_exc()
                    if event.key() == Qt.Key.Key_Backspace and obj.text() == "":
                        idx = self.cid_edits.index(obj)
                        if idx > 0:
                            prev = self.cid_edits[idx - 1]
                            prev.setFocus()
                            prev.clear()
                            try:
                                prev.selectAll()
                            except Exception as e:
                                traceback.print_exc()
                            return True
                        else:
                            # Update preview even when deleting within a field
                            self._update_pid_preview()
            # Note: explicit QEvent.Type.Paste branch is omitted for PyQt6 compatibility.
            # Paste is handled in the KeyPress branch via event.matches(QKeySequence.Paste).
        except Exception as e:
            traceback.print_exc()
        return super().eventFilter(obj, event)

    # Helpers
    def _set_text_if_exists(self, attr: str, text: str):
        try:
            w = getattr(self, attr, None)
            if w is not None:
                w.setText(text)
        except Exception as e:
            traceback.print_exc()

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
        except Exception as e:
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
        except Exception as e:
            traceback.print_exc()
            return ""

    def _fmt_pid(self, pid: str) -> str:
        try:
            digits = ''.join(ch for ch in str(pid) if ch.isdigit())
            if len(digits) != 13:
                return pid
            return f"{digits[0]}-{digits[1:5]}-{digits[5:10]}-{digits[10:12]}-{digits[12]}"
        except Exception as e:
            traceback.print_exc()
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
                except Exception as e:
                    traceback.print_exc()
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
                    except Exception as e:
                        traceback.print_exc()
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
            traceback.print_exc()
            print(f"Error collecting CID: {e}")

    def _update_pid_preview(self):
        try:
            digits = ''.join(e.text().strip() for e in getattr(self, 'cid_edits', []))
            if hasattr(self, 'cid_preview') and self.cid_preview is not None:
                self.cid_preview.setText(self._fmt_pid(digits))
        except Exception as e:
            traceback.print_exc()

    def _clear_results(self):
        try:
            # Clear CID edits
            for e in getattr(self, 'cid_edits', []) or []:
                try:
                    e.clear()
                except Exception:
                    pass
            # Clear preview
            try:
                if hasattr(self, 'cid_preview') and self.cid_preview is not None:
                    self.cid_preview.clear()
            except Exception:
                pass
            # Clear labels
            for attr in [
                'value_check_date','value_pid','value_tname','value_fname','value_lname',
                'value_nation','value_birth_date','value_sex','value_main_inscl','value_sub_inscl',
                'value_hosp_main','value_hosp_sub','value_right_no']:
                try:
                    w = getattr(self, attr, None)
                    if w is not None:
                        w.clear()
                except Exception:
                    pass
            # Clear raw response
            try:
                if hasattr(self, 'raw_text') and self.raw_text is not None:
                    self.raw_text.clear()
            except Exception:
                pass
            # Clear table/model
            try:
                if hasattr(self, 'result_table') and self.result_table is not None:
                    self.result_table.setModel(None)
            except Exception:
                pass
            # Focus first CID field
            try:
                edits = getattr(self, 'cid_edits', []) or []
                if edits:
                    edits[0].setFocus()
                    try:
                        edits[0].selectAll()
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            traceback.print_exc()

    # ===== SmartCard handlers: read only CID and fill inputs =====
    def _fill_cid_from_string(self, cid_text: str):
        try:
            digits = ''.join(ch for ch in str(cid_text) if ch.isdigit())[:13]
            if not digits:
                return
            # clear and fill each edit
            edits = getattr(self, 'cid_edits', [])
            for i, edit in enumerate(edits):
                try:
                    ch = digits[i] if i < len(digits) else ''
                    edit.setText(ch)
                except Exception:
                    traceback.print_exc()
            # focus last filled
            try:
                last_i = min(len(digits), len(edits)) - 1
                if last_i >= 0:
                    edits[last_i].setFocus()
                    try:
                        edits[last_i].selectAll()
                    except Exception:
                        pass
            except Exception:
                pass
            # update preview
            self._update_pid_preview()
            # auto-submit if fully filled (13 digits)
            if len(digits) == 13:
                try:
                    self._on_submit_cid()
                except Exception:
                    traceback.print_exc()
        except Exception as e:
            traceback.print_exc()

    def smc_state(self, info: dict):
        try:
            print(f"[SMC] state: {info}")
            state = (info or {}).get('state')
            if state == 'removed':
                # Clear CID and results on card removal
                self._clear_results()
        except Exception:
            traceback.print_exc()

    def smc_data(self, data: dict):
        try:
            print(f"[SMC] data: {data}")
            # Only care about citizen id
            cid = (data or {}).get('cid')
            if cid and str(cid).strip().lower() != 'err':
                self._fill_cid_from_string(str(cid))
        except Exception:
            traceback.print_exc()

    def smc_photo(self, data: dict):
        # Ignore photo per requirement (read CID only)
        try:
            try:
                img = (data or {}).get('img')
                if isinstance(img, (bytes, bytearray)):
                    print(f"[SMC] photo bytes: {len(img)}")
                else:
                    print(f"[SMC] photo: {type(img)}")
            except Exception:
                pass
        except Exception:
            traceback.print_exc()

    def closeEvent(self, event):
        try:
            if hasattr(self, 'smc') and self.smc is not None:
                try:
                    self.smc.stop()
                except Exception:
                    pass
                try:
                    if self.smc.isRunning():
                        self.smc.quit()
                        self.smc.wait(2000)
                except Exception:
                    pass
        except Exception:
            traceback.print_exc()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PersonalCheck()
    w.show()
    sys.exit(app.exec())
