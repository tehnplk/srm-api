import sys
import traceback
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QEvent, QSettings
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
        self.smc = SmartCardObserver(read_photo=False)
        self.smc.signal_data.connect(self.smc_data)
        self.smc.signal_photo.connect(self.smc_photo)
        self.smc.signal_state.connect(self.smc_state)
        
        # Initialize settings
        self.settings = QSettings("SRM_API", "MySQL_Settings")
        
        # Connect update button
        try:
            self.btn_update_his.clicked.connect(self.on_update_his)
        except Exception as e:
            traceback.print_exc()
            
        # Connect refresh token button
        try:
            self.btn_refresh_token.clicked.connect(self.on_refresh_token)
        except Exception as e:
            traceback.print_exc()
        
        # Store current eligibility data
        self.current_data = {}

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

            # Store current data for update
            self.current_data = data
            
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
            # focus last filled (do not select all; put caret at end)
            try:
                last_i = min(len(digits), len(edits)) - 1
                if last_i >= 0:
                    edits[last_i].setFocus()
                    try:
                        edits[last_i].setCursorPosition(len(edits[last_i].text()))
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

    def _get_db_config(self):
        return {
            "host": self.settings.value("host", "localhost"),
            "port": int(self.settings.value("port", 3306)),
            "user": self.settings.value("user", ""),
            "password": self.settings.value("password", ""),
            "database": self.settings.value("database", ""),
            "charset": "tis620",
            "connect_timeout": int(self.settings.value("timeout", 10)),
        }

    def _ensure_config_complete(self) -> bool:
        cfg = self._get_db_config()
        missing = [k for k in ("host", "user", "database") if not str(cfg.get(k, "")).strip()]
        if missing:
            QMessageBox.warning(self, "การตั้งค่าไม่ครบ", f"โปรดตั้งค่า: {', '.join(missing)} ในเมนู ตั้งค่า")
            return False
        return True

    def on_refresh_token(self):
        """Refresh SRM token"""
        try:
            refresh_token()
            QMessageBox.information(self, 'สำเร็จ', 'รีเฟรชโทเคนเรียบร้อยแล้ว')
            self._log("[SUCCESS] รีเฟรชโทเคนเรียบร้อย")
        except Exception as e:
            QMessageBox.warning(self, 'ล้มเหลว', f'การขอ token ใหม่เกิดข้อผิดพลาด:\n{e}')
            self._log(f"[ERROR] รีเฟรชโทเคนล้มเหลว: {e}")

    def on_update_his(self):
        """Update eligibility information to HIS database"""
        try:
            if not self.current_data:
                QMessageBox.warning(self, "ไม่มีข้อมูล", "กรุณาตรวจสอบสิทธิก่อนอัพเดท")
                return
                
            if not self._ensure_config_complete():
                return
                
            cid = self.current_data.get('pid')
            if not cid:
                QMessageBox.warning(self, "ไม่มีข้อมูล", "ไม่พบเลขบัตรประชาชน")
                return
                
            # Confirm update
            reply = QMessageBox.question(
                self, 
                "ยืนยันการอัพเดท", 
                f"ต้องการอัพเดทสิทธิใน HIS สำหรับ CID: {self._fmt_pid(cid)} หรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
                
            # Extract eligibility data
            funds = self.current_data.get('funds', [])
            f0 = funds[0] if funds else {}
            
            new_type = ""
            new_no = ""
            hospmain_hcode = None
            hospsub_hcode = None
            begin_date = None
            expire_date = None
            main_inscl_name = None
            sub_inscl_name = None
            
            # Extract data from API response
            try:
                # Prefer top-level fields
                subinscl_top = self.current_data.get('subinscl') or self.current_data.get('subInscl')
                cardid_top = self.current_data.get('cardId') or self.current_data.get('cardID')
                if subinscl_top:
                    if isinstance(subinscl_top, dict):
                        new_type = str(subinscl_top.get('id') or subinscl_top.get('name') or "")
                        sub_inscl_name = str(subinscl_top.get('name') or "")
                    else:
                        new_type = str(subinscl_top)
                if cardid_top:
                    new_no = str(cardid_top)
                    
                maininscl_top = self.current_data.get('mainInscl') or self.current_data.get('maininscl')
                if isinstance(maininscl_top, dict):
                    main_inscl_name = str(maininscl_top.get('name') or "")
                    
                # Optional top-level hosp codes and dates
                hm_top = self.current_data.get('hospMain') or {}
                if isinstance(hm_top, dict):
                    hospmain_hcode = hm_top.get('hcode')
                hs_top = self.current_data.get('hospSub') or {}
                if isinstance(hs_top, dict):
                    hospsub_hcode = hs_top.get('hcode')
                begin_date = self.current_data.get('startDateTime')
                expire_date = self.current_data.get('expireDateTime')
                
                # Fallback to first fund entry
                if ((not new_type) or (not new_no)) and isinstance(funds, list) and funds:
                    f0 = funds[0] if isinstance(funds[0], dict) else {}
                    if not new_type:
                        sub = f0.get('subInscl') if isinstance(f0.get('subInscl'), dict) else None
                        if sub:
                            new_type = str(sub.get('id') or sub.get('name') or "")
                            sub_inscl_name = str(sub.get('name') or "")
                    if not new_no:
                        new_no = str(f0.get('cardId') or f0.get('cardID') or "")
                    
                    hm = f0.get('hospMain') if isinstance(f0.get('hospMain'), dict) else None
                    if hm and not hospmain_hcode:
                        hospmain_hcode = hm.get('hcode')
                    hs = f0.get('hospSub') if isinstance(f0.get('hospSub'), dict) else None
                    if hs and not hospsub_hcode:
                        hospsub_hcode = hs.get('hcode')
                    if not begin_date:
                        begin_date = f0.get('startDateTime')
                    if not expire_date:
                        expire_date = f0.get('expireDateTime')
                        
            except Exception as e:
                traceback.print_exc()
                
            # Update database
            import pymysql
            cfg = self._get_db_config()
            system = str(self.settings.value("system", "jhcis")).strip().lower()
            
            with pymysql.connect(**cfg) as conn:
                with conn.cursor() as cur:
                    if system == 'hosxp':
                        # Update person table
                        sql_person = (
                            "UPDATE person SET "
                            "pttype=%s, "
                            "pttype_begin_date=DATE(%s), "
                            "pttype_expire_date=DATE(%s), "
                            "pttype_hospmain=%s, "
                            "pttype_hospsub=%s, "
                            "pttype_no=%s, "
                            "last_update_pttype=NOW() "
                            "WHERE cid=%s"
                        )
                        params_person = [
                            new_type or None,
                            begin_date or None,
                            expire_date or None,
                            hospmain_hcode or None,
                            hospsub_hcode or None,
                            new_no or None,
                            cid,
                        ]
                        cur.execute(sql_person, params_person)
                        
                        # Update patient table
                        sql_patient = (
                            "UPDATE patient SET "
                            "pttype=%s, pttype_no=%s, "
                            "pttype_hospmain=%s, pttype_hospsub=%s, "
                            "last_update=NOW() "
                            "WHERE cid=%s"
                        )
                        params_patient = [
                            new_type or None,
                            new_no or None,
                            hospmain_hcode or None,
                            hospsub_hcode or None,
                            cid,
                        ]
                        cur.execute(sql_patient, params_patient)
                        
                        # Update today's ovst
                        sql_ovst = (
                            "UPDATE ovst o "
                            "JOIN patient p ON p.hn = o.hn "
                            "SET o.pttype=%s, o.pttypeno=%s, o.hospmain=%s, o.hospsub=%s "
                            "WHERE DATE(o.vstdate)=CURDATE() AND p.cid=%s"
                        )
                        params_ovst = [
                            new_type or None,
                            new_no or None,
                            hospmain_hcode or None,
                            hospsub_hcode or None,
                            cid,
                        ]
                        cur.execute(sql_ovst, params_ovst)
                        
                    elif system == 'jhcis':
                        # Update person rights (JHCIS)
                        sets = []
                        params = []
                        if new_type:
                            sets.append("rightcode=%s"); params.append(new_type)
                        if new_no:
                            sets.append("rightno=%s"); params.append(new_no)
                        if hospmain_hcode is not None:
                            sets.append("hosmain=%s"); params.append(hospmain_hcode)
                        if hospsub_hcode is not None:
                            sets.append("hossub=%s"); params.append(hospsub_hcode)
                        if begin_date:
                            sets.append("datestart=DATE(%s)"); params.append(begin_date)
                        if expire_date:
                            sets.append("dateexpire=DATE(%s)"); params.append(expire_date)
                        if sets:
                            sets.append("dateupdate=NOW()")
                            params.append(cid)
                            sql = "UPDATE person SET " + ", ".join(sets) + " WHERE idcard=%s"
                            cur.execute(sql, params)
                            
                        # Update today's visit by pid (JHCIS)
                        try:
                            cur.execute("SELECT pid FROM person WHERE idcard=%s LIMIT 1", (cid,))
                            rpid = cur.fetchone()
                            if rpid and len(rpid) > 0:
                                pid_val = rpid[0]
                                sql_visit = (
                                    "UPDATE visit SET "
                                    "rightcode=%s, rightno=%s, hosmain=%s, hossub=%s, "
                                    "main_inscl=%s, sub_inscl=%s, dateupdate=NOW() "
                                    "WHERE pid=%s AND visitdate=CURDATE()"
                                )
                                params_visit = [
                                    new_type or None,
                                    new_no or None,
                                    hospmain_hcode or None,
                                    hospsub_hcode or None,
                                    main_inscl_name or None,
                                    sub_inscl_name or None,
                                    pid_val,
                                ]
                                cur.execute(sql_visit, params_visit)
                        except Exception:
                            pass
                            
                conn.commit()
                
            self._log(f"[SUCCESS] อัพเดทสิทธิใน HIS เรียบร้อยสำหรับ CID: {self._fmt_pid(cid)}")
            QMessageBox.information(self, "สำเร็จ", f"อัพเดทสิทธิใน HIS เรียบร้อย\nCID: {self._fmt_pid(cid)}")
            
        except Exception as e:
            traceback.print_exc()
            self._log(f"[ERROR] อัพเดทสิทธิล้มเหลว: {e}")
            QMessageBox.critical(self, "ผิดพลาด", f"อัพเดทสิทธิล้มเหลว:\n{e}")

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
