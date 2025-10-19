import os
import json
from datetime import datetime
from typing import Optional

import requests


def read_token() -> str:
    token_file = os.path.join(os.environ['USERPROFILE'], 'SRM Smart Card Single Sign-On', 'token.txt')
    with open(token_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('access-token='):
                return line.split('=', 1)[1]
    raise ValueError('ไม่พบ access-token ในไฟล์ token.txt')


def ensure_srm_check_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS srm_check (
                cid VARCHAR(20) PRIMARY KEY,
                check_date DATETIME NULL,
                fund TEXT NULL,
                maininscl VARCHAR(255) NULL,
                maininscl_name VARCHAR(255) NULL,
                subinscl VARCHAR(255) NULL,
                subinscl_name VARCHAR(255) NULL,
                card_id VARCHAR(255) NULL,
                death_date DATE NULL,
                status VARCHAR(255) NULL
            ) CHARACTER SET tis620 COLLATE tis620_thai_ci
            """
        )
    conn.commit()


def was_checked_today(conn, cid: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1 FROM srm_check
            WHERE cid = %s AND DATE(check_date) = CURDATE()
            LIMIT 1
            """,
            (cid,)
        )
        row = cur.fetchone()
        return bool(row)


def _has_hosxp_death_flag(conn) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'patient'
                  AND COLUMN_NAME = 'death'
                LIMIT 1
                """
            )
            return bool(cur.fetchone())
    except Exception:
        return False


def is_patient_dead(conn, cid: str) -> bool:
    with conn.cursor() as cur:
        if _has_hosxp_death_flag(conn):
            cur.execute(
                """
                SELECT death FROM patient WHERE cid=%s LIMIT 1
                """,
                (cid,)
            )
            row = cur.fetchone()
            if not row:
                return False
            death_val = row[0]
            return isinstance(death_val, str) and death_val.upper() == 'Y'
        else:
            # JHCIS: check person.dischargetype (9 = dead)
            try:
                cur.execute(
                    """
                    SELECT 1 FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'person'
                      AND COLUMN_NAME = 'dischargetype'
                    LIMIT 1
                    """
                )
                if not cur.fetchone():
                    return False
                cur.execute(
                    """
                    SELECT dischargetype FROM person WHERE idcard=%s LIMIT 1
                    """,
                    (cid,)
                )
                row = cur.fetchone()
                if not row:
                    return False
                dt = row[0]
                if dt is None:
                    return False
                # Consider dead when dischargetype is not '9'
                return str(dt).strip() != '9'
            except Exception:
                return False


def _normalize_check_date(check_date: Optional[str]) -> Optional[str]:
    if isinstance(check_date, str) and check_date:
        try:
            dt = datetime.fromisoformat(check_date.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return check_date.replace('T', ' ').replace('Z', '').split('.')[0]
    return None


def _normalize_death_date(death_date: Optional[str]) -> Optional[str]:
    if isinstance(death_date, str) and death_date:
        try:
            if 'T' in death_date or ' ' in death_date:
                dtx = datetime.fromisoformat(death_date.replace('Z', '+00:00'))
                return dtx.strftime('%Y-%m-%d')
            return death_date.split('T')[0].split(' ')[0]
        except Exception:
            try:
                dtx = datetime.strptime(death_date, '%Y-%m-%d')
                return dtx.strftime('%Y-%m-%d')
            except Exception:
                return None
    return None


def upsert_srm_check(conn, cid: str, check_date: Optional[str], death_date: Optional[str], funds: list, status: Optional[int] = None) -> None:
    norm_dt = _normalize_check_date(check_date)
    norm_death = _normalize_death_date(death_date)
    fund_text = json.dumps(funds or [], ensure_ascii=False)
    # Extract from the first fund record (can change to latest if desired)
    maininscl_id = None
    maininscl_name = None
    subinscl_id = None
    subinscl_name = None
    card_id = None
    try:
        if isinstance(funds, list) and funds:
            f0 = funds[0]
            main = f0.get('mainInscl') or {}
            sub = f0.get('subInscl') or {}
            maininscl_id = (main.get('id') or None)
            maininscl_name = (main.get('name') or None)
            subinscl_id = (sub.get('id') or None)
            subinscl_name = (sub.get('name') or None)
            card_id = f0.get('cardId') or None
    except Exception:
        maininscl_id = maininscl_name = subinscl_id = subinscl_name = card_id = None
    with conn.cursor() as cur:
        cur.execute(
            """
            REPLACE INTO srm_check (cid, check_date, fund, maininscl, maininscl_name, subinscl, subinscl_name, card_id, death_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (cid, norm_dt, fund_text, maininscl_id, maininscl_name, subinscl_id, subinscl_name, card_id, norm_death, None if status is None else str(status))
        )
    conn.commit()


def update_patient_death(conn, cid: str) -> None:
    # Only update for HOSxP schema with patient.death flag
    if not _has_hosxp_death_flag(conn):
        return
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE patient SET death='Y' WHERE cid=%s
            """,
            (cid,)
        )
    conn.commit()


def call_right_search(token: str, cid: str) -> requests.Response:
    headers = { 'Authorization': f'Bearer {token}' }
    url = f"https://srm.nhso.go.th/api/ucws/v1/right-search?pid={cid}"
    return requests.get(url, headers=headers)


def refresh_token():
    token_file = os.path.join(os.environ['USERPROFILE'], 'SRM Smart Card Single Sign-On', 'token.txt')
    # Read existing refresh-token from file
    refresh_tok = None
    with open(token_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('refresh-token='):
                refresh_tok = line.split('=', 1)[1]
                break
    if not refresh_tok:
        raise ValueError("ไม่พบ refresh-token ในไฟล์")

    url = "https://srmportal.nhso.go.th/api/scard/access-token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"refresh_token": refresh_tok}

    # Request new tokens
    resp = requests.post(url, headers=headers, data=data)

    # Do not write file if error
    if not resp.ok:
        raise RuntimeError("การขอ token ใหม่เกิดข้อผิดพลาด")

    text = (resp.text or "").strip()

    # Try JSON first
    access_line = None
    refresh_line = None
    try:
        js = resp.json()
        # Accept common keys
        acc = js.get('access_token') or js.get('access-token') or js.get('accessToken')
        ref = js.get('refresh_token') or js.get('refresh-token') or js.get('refreshToken')
        if acc:
            access_line = f"access-token={acc}"
        if ref:
            refresh_line = f"refresh-token={ref}"
    except Exception:
        # Fallback: parse plain text lines
        for ln in text.splitlines():
            s = ln.strip()
            if s.startswith('access-token=') and not access_line:
                access_line = s
            elif s.startswith('refresh-token=') and not refresh_line:
                refresh_line = s

    if not access_line:
        # No valid access token, do not overwrite file
        raise RuntimeError("การขอ token ใหม่เกิดข้อผิดพลาด")

    # Write back only normalized lines we have
    out_lines = [access_line]
    if refresh_line:
        out_lines.append(refresh_line)
    with open(token_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(out_lines) + "\n")

    return access_line.split('=', 1)[1]


