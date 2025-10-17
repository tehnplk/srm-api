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
url = "https://srm.nhso.go.th/api/scard/access-token"

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "refresh-token": refresh_token
}

print(f"กำลังขอ access token ใหม่ด้วย refresh token...")

try:
    response = requests.post(url, headers=headers, data=data)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        new_access_token = result.get('access_token')

        if new_access_token:
            print(f"ได้ access token ใหม่แล้ว: {new_access_token[:50]}...")
            print("สำเร็จ!")
        else:
            print("ไม่พบ access_token ใน response")
            print(f"Response: {response.text}")
    else:
        print(f"การขอ token ใหม่ล้มเหลว: HTTP {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")
