# Buffet Ordering System

ระบบสั่งอาหาร Buffet แบบจำกัดเวลา 1 ชั่วโมง 45 นาที

## 🚀 ฟีเจอร์หลัก

- ⏱️ จับเวลาอัตโนมัติ 105 นาที (1 ชม 45 นาที)
- 🍽️ เมนูอาหารหลากหลายหมวดหมู่
- 📱 หน้าเว็บที่ใช้งานง่าย สวยงาม
- ✅ เช็คบิลได้ทันที และปิดรับออเดอร์อัตโนมัติ
- 🔔 แจ้งเตือนเมื่อเวลาใกล้หมด
- 💾 เก็บข้อมูลใน Database

## 🛠️ Technology Stack

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- SQLite (Development) / PostgreSQL (Production)
- Uvicorn ASGI Server

### Frontend
- React 18
- Vite
- Axios
- CSS3 with Gradients

### Deployment
- Docker & Docker Compose
- AWS Elastic Beanstalk / Lambda
- AWS RDS (PostgreSQL)
- AWS Amplify / S3 + CloudFront

## 📁 โครงสร้างโปรเจค

```
buffet-ordering-system/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Backend Docker image
│   └── .env.example           # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── main.jsx           # React entry point
│   │   └── index.css          # Global styles
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── Dockerfile             # Frontend Docker image
│   └── nginx.conf             # Nginx configuration
├── docker-compose.yml         # Docker Compose config
├── .gitignore
└── README.md
```

## 🚀 การติดตั้งและรัน

### วิธีที่ 1: ใช้ Docker Compose (แนะนำ)

```bash
# Clone repository
git clone https://github.com/somchx/buffet-ordering-system.git
cd buffet-ordering-system

# Build and run
docker-compose up -d

# Seed sample menu data
curl -X POST http://localhost:8000/api/seed
```

เปิดเว็บที่: http://localhost

### วิธีที่ 2: รันแยกส่วน

#### Backend

```bash
cd backend

# สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# สร้างไฟล์ .env
cp .env.example .env

# รัน server
python main.py
```

Backend จะรันที่: http://localhost:8000

#### Frontend

```bash
cd frontend

# ติดตั้ง dependencies
npm install

# สร้างไฟล์ .env
cp .env.example .env

# รัน development server
npm run dev
```

Frontend จะรันที่: http://localhost:3000

## 📡 API Endpoints

### Orders
- `POST /api/orders/start` - เริ่มออเดอร์ใหม่
- `GET /api/orders/{order_id}` - ดูข้อมูลออเดอร์
- `POST /api/orders/{order_id}/items` - เพิ่มรายการอาหาร
- `POST /api/orders/{order_id}/checkout` - เช็คบิล

### Menu
- `GET /api/menu` - ดูเมนูทั้งหมด
- `POST /api/menu` - เพิ่มเมนูใหม่
- `PUT /api/menu/{item_id}` - แก้ไขเมนู
- `DELETE /api/menu/{item_id}` - ลบเมนู

### Utility
- `POST /api/seed` - สร้างข้อมูลตัวอย่าง

API Documentation: http://localhost:8000/docs

## 💾 Database Schema

### Orders Table
```sql
- id (INTEGER, PRIMARY KEY)
- table_number (STRING, NULLABLE)
- start_time (DATETIME)
- end_time (DATETIME)
- is_active (BOOLEAN)
- is_checked_out (BOOLEAN)
- total_amount (FLOAT)
```

### Menu Items Table
```sql
- id (INTEGER, PRIMARY KEY)
- name (STRING)
- category (STRING)
- price (FLOAT)
- image_url (STRING, NULLABLE)
- is_available (BOOLEAN)
```

### Order Items Table
```sql
- id (INTEGER, PRIMARY KEY)
- order_id (INTEGER, FOREIGN KEY)
- menu_item_id (INTEGER, FOREIGN KEY)
- quantity (INTEGER)
- created_at (DATETIME)
```

## 🌐 การ Deploy ขึ้น AWS

ดูคำแนะนำโดยละเอียดในไฟล์ `AWS_DEPLOYMENT.md`

### สรุปขั้นตอน

1. **Setup AWS CLI**
   ```bash
   aws configure
   ```

2. **Deploy Backend (Elastic Beanstalk)**
   ```bash
   cd backend
   eb init -p python-3.11 buffet-backend --region us-east-1
   eb create buffet-backend-env
   ```

3. **Deploy Frontend (Amplify)**
   ```bash
   cd frontend
   npm install -g @aws-amplify/cli
   amplify init
   amplify add hosting
   amplify publish
   ```

## 🔧 การตั้งค่า Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./buffet.db
# For production:
# DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/buffet_db
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
# For production:
# VITE_API_URL=https://your-api-domain.com
```

## 🧪 การทดสอบ

```bash
# Test backend API
curl http://localhost:8000/api/menu

# Test start order
curl -X POST http://localhost:8000/api/orders/start \
  -H "Content-Type: application/json" \
  -d '{"table_number": "A1"}'
```

## 📝 License

MIT License

## 👨‍💻 Author

Created by somchx

## 🤝 Contributing

Pull requests are welcome!

---

Made with ❤️ for buffet lovers
