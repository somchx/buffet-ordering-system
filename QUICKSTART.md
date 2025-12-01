# คำสั่งสำหรับรันโปรเจค - Quick Start Guide

## 🚀 วิธีรันโปรเจคแบบง่าย (Docker Compose)

### 1. Clone โปรเจค
```bash
git clone https://github.com/somchx/buffet-ordering-system.git
cd buffet-ordering-system
```

### 2. รันด้วย Docker Compose
```bash
# Build และรัน
docker-compose up -d

# รอสักครู่แล้วเปิดเบราว์เซอร์
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 3. สร้างข้อมูลตัวอย่าง (Menu)
```bash
curl -X POST http://localhost:8000/api/seed
```

### 4. ทดสอบระบบ
- เปิดเบราว์เซอร์: http://localhost
- กดปุ่ม "เริ่มสั่งอาหาร"
- เลือกเมนูอาหาร
- ดูเวลานับถอยหลัง
- กด "เช็คบิล" เมื่อต้องการจบ

### 5. หยุดระบบ
```bash
docker-compose down
```

---

## 🛠️ วิธีรันแบบแยกส่วน (Development)

### Backend (FastAPI)

```bash
# 1. ไปที่โฟลเดอร์ backend
cd backend

# 2. สร้าง virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# หรือ
venv\Scripts\activate     # Windows

# 4. ติดตั้ง dependencies
pip install -r requirements.txt

# 5. สร้างไฟล์ .env
cp .env.example .env

# 6. รัน server
python main.py

# หรือ
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Backend จะรันที่: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Frontend (React + Vite)

```bash
# 1. เปิด terminal ใหม่ ไปที่โฟลเดอร์ frontend
cd frontend

# 2. ติดตั้ง dependencies
npm install

# 3. สร้างไฟล์ .env
cp .env.example .env

# 4. รัน development server
npm run dev

# Frontend จะรันที่: http://localhost:3000
```

### สร้างข้อมูลตัวอย่าง

```bash
# เปิด terminal ใหม่
curl -X POST http://localhost:8000/api/seed
```

---

## 🧪 ทดสอบ API ด้วย curl

### สร้างออเดอร์ใหม่
```bash
curl -X POST http://localhost:8000/api/orders/start \
  -H "Content-Type: application/json" \
  -d '{"table_number": "A1"}'

# จะได้ order_id กลับมา เช่น: {"id": 1, ...}
```

### ดูรายการเมนู
```bash
curl http://localhost:8000/api/menu
```

### เพิ่มอาหารในออเดอร์
```bash
curl -X POST http://localhost:8000/api/orders/1/items \
  -H "Content-Type: application/json" \
  -d '{"menu_item_id": 1, "quantity": 2}'
```

### ดูข้อมูลออเดอร์
```bash
curl http://localhost:8000/api/orders/1
```

### เช็คบิล
```bash
curl -X POST http://localhost:8000/api/orders/1/checkout
```

---

## 📦 Build สำหรับ Production

### Build Backend
```bash
cd backend
docker build -t buffet-backend .
docker run -p 8000:8000 buffet-backend
```

### Build Frontend
```bash
cd frontend
npm run build
# ไฟล์ build จะอยู่ใน folder dist/

# ทดสอบ production build
npm run preview
```

---

## 🌐 Deploy ขึ้น AWS

### Push โค้ดขึ้น GitHub (เสร็จแล้ว)
```bash
git status
git add .
git commit -m "Update code"
git push origin main
```

### Deploy ขึ้น AWS
ดูคำแนะนำโดยละเอียดใน `AWS_DEPLOYMENT.md`

**สรุปขั้นตอน:**

1. **Setup AWS CLI**
```bash
# ติดตั้ง AWS CLI
brew install awscli  # macOS
# หรือดาวน์โหลดจาก aws.amazon.com/cli

# Configure
aws configure
# ใส่ Access Key, Secret Key, Region (us-east-1)
```

2. **Deploy Backend (Elastic Beanstalk)**
```bash
cd backend

# ติดตั้ง EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 buffet-backend --region us-east-1

# Create environment
eb create buffet-backend-env

# Deploy
eb deploy

# ดู URL
eb open
```

3. **Deploy Frontend (Amplify)**
```bash
cd frontend

# ติดตั้ง Amplify CLI
npm install -g @aws-amplify/cli

# Configure
amplify configure

# Initialize
amplify init

# Add hosting
amplify add hosting

# Publish
amplify publish
```

---

## 🐛 Troubleshooting

### Backend ไม่สามารถเชื่อมต่อ Database
```bash
# ตรวจสอบ .env file
cat backend/.env

# ลอง connect ด้วย sqlite3
cd backend
sqlite3 buffet.db
.tables
.quit
```

### Frontend ไม่สามารถเชื่อมต่อ Backend
```bash
# ตรวจสอบ .env file
cat frontend/.env

# ตรวจสอบว่า backend รันอยู่หรือไม่
curl http://localhost:8000/

# ตรวจสอบ CORS
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://localhost:8000/api/menu
```

### Docker ไม่ทำงาน
```bash
# ตรวจสอบ Docker running
docker ps

# ดู logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port ถูกใช้งานอยู่
```bash
# ตรวจสอบ port 8000
lsof -i :8000

# ปิด process ที่ใช้ port
kill -9 <PID>

# หรือเปลี่ยน port ใน docker-compose.yml
```

---

## 📊 ตรวจสอบสถานะระบบ

### ตรวจสอบ Backend
```bash
# Health check
curl http://localhost:8000/

# ดูจำนวน orders
curl http://localhost:8000/api/orders/1 | python -m json.tool

# ดูจำนวน menu items
curl http://localhost:8000/api/menu | python -m json.tool | grep -c "id"
```

### ตรวจสอบ Docker
```bash
# ดู containers ที่รันอยู่
docker ps

# ดู logs
docker logs buffet-backend
docker logs buffet-frontend

# เข้าไปใน container
docker exec -it buffet-backend bash
```

---

## 🔄 Update โปรเจค

### Pull code ใหม่จาก GitHub
```bash
git pull origin main
```

### Update dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Restart ทุกอย่าง
```bash
# Docker
docker-compose restart

# หรือ rebuild
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 📝 เพิ่มเมนูอาหารใหม่

### ผ่าน API
```bash
curl -X POST http://localhost:8000/api/menu \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ข้าวมันไก่",
    "category": "อาหารจานหลัก",
    "price": 0,
    "image_url": "https://example.com/image.jpg",
    "is_available": true
  }'
```

### แก้ไขเมนู
```bash
curl -X PUT http://localhost:8000/api/menu/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ข้าวผัดพิเศษ",
    "category": "อาหารจานหลัก",
    "price": 0,
    "is_available": true
  }'
```

### ลบเมนู (ซ่อน)
```bash
curl -X DELETE http://localhost:8000/api/menu/1
```

---

## 💡 Tips & Best Practices

1. **Development**: ใช้วิธีรันแยกส่วน (Backend + Frontend แยก terminal)
2. **Testing**: ใช้ Docker Compose เพื่อทดสอบแบบ production-like
3. **Production**: Deploy ขึ้น AWS ตาม AWS_DEPLOYMENT.md
4. **Database**: ใช้ SQLite สำหรับ dev, PostgreSQL สำหรับ production
5. **Environment Variables**: อย่าลืมแก้ .env ให้ถูกต้อง
6. **CORS**: ตรวจสอบ CORS settings ใน backend/main.py
7. **Monitoring**: ใช้ CloudWatch สำหรับ AWS deployment
8. **Backup**: Backup database เป็นประจำ

---

## 🎉 ทดสอบว่าทุกอย่างทำงาน

### Checklist
- [ ] Backend API รันได้ (http://localhost:8000)
- [ ] API Docs เข้าได้ (http://localhost:8000/docs)
- [ ] Frontend เว็บเข้าได้ (http://localhost:3000)
- [ ] สามารถเริ่มออเดอร์ได้
- [ ] สามารถเลือกเมนูอาหารได้
- [ ] Timer นับถอยหลังทำงาน
- [ ] สามารถเช็คบิลได้
- [ ] เวลาหมดแล้วไม่สามารถสั่งได้
- [ ] Push ขึ้น GitHub สำเร็จ

---

## 📞 ช่วยเหลือเพิ่มเติม

- GitHub: https://github.com/somchx/buffet-ordering-system
- Issues: https://github.com/somchx/buffet-ordering-system/issues
- Documentation: README.md, AWS_DEPLOYMENT.md

Made with ❤️ Happy Coding!
