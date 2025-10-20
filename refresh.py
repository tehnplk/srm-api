import os
import requests
import json


# อ่าน refresh_token จากไฟล์
token_file = os.path.join(os.environ['USERPROFILE'], 'SRM Smart Card Single Sign-On', 'token.txt')
with open(token_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('refresh-token='):
            refresh_token = line.split('=', 1)[1]
            break
    else:
        raise ValueError("ไม่พบ refresh-token ในไฟล์")

# ขอ access token ใหม่โดยใช้ refresh token
url = "https://srmportal.nhso.go.th/api/scard/access-token"

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "refresh_token": refresh_token
}

print(f"กำลังขอ access token ใหม่ด้วย refresh token...")

response = requests.post(url, headers=headers, data=data)
print(f"สถานะคำขอ: {response.status_code}")
print(f"ประเภทข้อมูล: {response.headers.get('Content-Type', '')}")
new_access_token = None
# พยายามแปลงเป็น JSON เพื่อตรวจสอบ error
try:
    parsed = response.json()
    print("ผลลัพธ์จาก API (JSON):")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    # ถ้า API ส่ง error กลับมา ไม่ต้องเขียนทับไฟล์
    if isinstance(parsed, dict) and (
        'error' in parsed or 'error_description' in parsed
    ):
        print("ข้ามการบันทึกโทเค่นเนื่องจาก API แจ้งข้อผิดพลาด")
        parsed = None
    elif isinstance(parsed, dict):
        # เผื่อกรณี API คืน access token ในฟิลด์
        for k in ("access_token", "access-token", "token"):
            if k in parsed and isinstance(parsed[k], str) and parsed[k].strip():
                new_access_token = parsed[k].strip()
                break
except Exception:
    parsed = None
# หากไม่ใช่ JSON หรือไม่มี error ให้ใช้ข้อความดิบเป็นโทเค่น (เช่น text/plain)
if new_access_token is None and parsed is None:
    body_text = response.text.strip()
    if body_text:
        print("ผลลัพธ์จาก API (ข้อความดิบ):")
        print(body_text)
        # พอใช้เป็นโทเค่นได้เมื่อไม่ใช่ JSON error
        new_access_token = body_text

# เขียนกลับเฉพาะค่า access-token โดยรักษาบรรทัดอื่น ๆ ไว้ (เช่น refresh-token)
if new_access_token:
    # อ่านบรรทัดทั้งหมดก่อน
    with open(token_file, 'r', encoding='utf-8') as fr:
        lines = fr.readlines()
    found = False
    new_lines = []
    for line in lines:
        raw = line.rstrip('\n')
        if raw.startswith('access-token='):
            new_lines.append(f"access-token={new_access_token}\n")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"access-token={new_access_token}\n")
    with open(token_file, 'w', encoding='utf-8') as fw:
        fw.writelines(new_lines)
else:
    # ไม่มีโทเค่นใหม่ให้เขียน (เช่นกรณี error) — ไม่เขียนทับไฟล์
    pass
