import gdown

# ตัวอย่าง URL ที่แชร์: https://drive.google.com/file/d/FILE_ID_HERE/view?usp=sharing
file_id = '129PWweSHyLOHcqLZ9iF7-MDvrJ0dOLJ4' # แทนที่ด้วย ID ไฟล์จริงของคุณ
output_path = 'myfile.zip' # เช่น 'data.zip' หรือ 'image.jpg'

try:
    gdown.download(id=file_id, output=output_path, quiet=False)
    print(f"ดาวน์โหลดไฟล์ '{output_path}' สำเร็จ")
except Exception as e:
    print(f"เกิดข้อผิดพลาดในการดาวน์โหลด: {e}")