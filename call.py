import requests
import json
import os

pid = "3650100813118"
pid = "3650101207220"
pid = "3660700517161"
url = f"https://srm.nhso.go.th/api/ucws/v1/right-search?pid={pid}"

# อ่าน token จากไฟล์
token_file = os.path.join(os.environ['USERPROFILE'], 'SRM Smart Card Single Sign-On', 'token.txt')
with open(token_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('access-token='):
            token = line.split('=', 1)[1]
            break
    else:
        raise ValueError("ไม่พบ access-token ในไฟล์")

#print(token)

headers = {
    "Authorization": f"Bearer {token}"
}
response = requests.get(url, headers=headers)
if  response.status_code == 200:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
else:
    print(f"Error: {response.status_code}")
