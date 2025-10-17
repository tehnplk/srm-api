# SRM API - ระบบจัดการข้อมูล

PyQt6 desktop application สำหรับจัดการข้อมูลประชากรและผู้รับบริการ

## คุณสมบัติ

- **เมนูหลัก:**
  - File → ประชากร, ผู้รับบริการ, Setting
  - Help → เกี่ยวกับ
- **Toolbar** พร้อมปุ่มลัดสำหรับฟังก์ชันหลัก
- **Status Bar** แสดงสถานะการทำงาน
- **UI สมัยใหม่** ด้วย CSS styling

## การติดตั้ง

1. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
# หรือใช้ uv
uv sync
```

2. รันโปรแกรม:
```bash
python main_window.py
```

## โครงสร้างโปรแกรม

- `main_window.py` - หน้าต่างหลักของโปรแกรม
- `pyproject.toml` - การจัดการ dependencies
- `call.py` - API calls (existing)
- `refrsh.py` - Refresh functionality (existing)

## การพัฒนาต่อ

โปรแกรมนี้เป็นโครงสร้างพื้นฐาน สามารถพัฒนาต่อได้โดย:
1. เพิ่มหน้าจอสำหรับจัดการประชากร
2. เพิ่มหน้าจอสำหรับจัดการผู้รับบริการ  
3. เพิ่มหน้าตั้งค่าระบบ
4. เชื่อมต่อกับ API backend
5. เพิ่มฐานข้อมูล

## เทคโนโลยี

- Python 3.12+
- PyQt6
- Modern CSS styling