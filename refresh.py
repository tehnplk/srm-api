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

print(refresh_token)
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
new_access_token = response.text.strip()
print(new_access_token)
with open(token_file, 'w', encoding='utf-8') as f:
    f.write(f"{new_access_token}\n")

