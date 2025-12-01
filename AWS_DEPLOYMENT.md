# AWS Deployment Guide - Buffet Ordering System

คู่มือการ Deploy ระบบขึ้น AWS แบบละเอียด

## 📋 Prerequisites

1. **AWS Account** - สมัครที่ https://aws.amazon.com
2. **AWS CLI** - ติดตั้ง AWS Command Line Interface
3. **Git** - สำหรับ version control
4. **Docker** (Optional) - สำหรับ local testing

## 🔧 Setup AWS CLI

### ติดตั้ง AWS CLI

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download and install from: https://aws.amazon.com/cli/
```

### Configure AWS Credentials

```bash
aws configure
```

จะถูกถามข้อมูล:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1` (แนะนำ)
- Default output format: `json`

## 🗄️ ส่วนที่ 1: Setup Database (RDS PostgreSQL)

### 1.1 สร้าง RDS Instance

```bash
# สร้าง Security Group สำหรับ RDS
aws ec2 create-security-group \
  --group-name buffet-db-sg \
  --description "Security group for Buffet RDS"

# เปิด port 5432 (PostgreSQL)
aws ec2 authorize-security-group-ingress \
  --group-name buffet-db-sg \
  --protocol tcp \
  --port 5432 \
  --cidr 0.0.0.0/0

# สร้าง RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier buffet-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourSecurePassword123! \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --publicly-accessible \
  --backup-retention-period 7
```

### 1.2 รอให้ RDS พร้อมใช้งาน

```bash
# ตรวจสอบสถานะ
aws rds describe-db-instances \
  --db-instance-identifier buffet-db \
  --query 'DBInstances[0].DBInstanceStatus'

# ดู endpoint
aws rds describe-db-instances \
  --db-instance-identifier buffet-db \
  --query 'DBInstances[0].Endpoint.Address'
```

บันทึก endpoint ที่ได้ เช่น: `buffet-db.xxxxx.us-east-1.rds.amazonaws.com`

## 🚀 ส่วนที่ 2: Deploy Backend (Elastic Beanstalk)

### 2.1 ติดตั้ง EB CLI

```bash
pip install awsebcli
```

### 2.2 เตรียม Backend

```bash
cd backend

# สร้างไฟล์ .env สำหรับ production
cat > .env << EOF
DATABASE_URL=postgresql://admin:YourSecurePassword123!@buffet-db.xxxxx.us-east-1.rds.amazonaws.com:5432/postgres
EOF
```

### 2.3 Initialize Elastic Beanstalk

```bash
# Initialize EB application
eb init -p python-3.11 buffet-backend --region us-east-1

# สร้าง environment
eb create buffet-backend-env \
  --instance-type t3.small \
  --envvars DATABASE_URL="postgresql://admin:YourSecurePassword123!@buffet-db.xxxxx.us-east-1.rds.amazonaws.com:5432/postgres"
```

### 2.4 Deploy Backend

```bash
# Deploy
eb deploy

# เปิด URL
eb open

# ดู logs
eb logs
```

### 2.5 Seed ข้อมูลตัวอย่าง

```bash
# ดู URL ของ backend
EB_URL=$(eb status | grep "CNAME" | awk '{print $2}')

# Seed data
curl -X POST http://$EB_URL/api/seed
```

บันทึก Backend URL เช่น: `buffet-backend-env.xxxxx.us-east-1.elasticbeanstalk.com`

## 🌐 ส่วนที่ 3: Deploy Frontend (AWS Amplify)

### 3.1 ติดตั้ง Amplify CLI

```bash
npm install -g @aws-amplify/cli
amplify configure
```

### 3.2 แก้ไข Frontend Config

```bash
cd ../frontend

# แก้ไข .env เพื่อชี้ไปที่ backend
cat > .env << EOF
VITE_API_URL=http://buffet-backend-env.xxxxx.us-east-1.elasticbeanstalk.com
EOF
```

### 3.3 Build Frontend

```bash
npm install
npm run build
```

### 3.4 Deploy ด้วย Amplify

```bash
# Initialize Amplify
amplify init

# ตอบคำถาม:
# - Enter a name: buffet-frontend
# - Environment: production
# - Default editor: VSCode
# - App type: javascript
# - Framework: react
# - Source directory: src
# - Distribution directory: dist
# - Build command: npm run build
# - Start command: npm run dev

# เพิ่ม hosting
amplify add hosting

# เลือก:
# - Hosting with Amplify Console
# - Manual deployment

# Publish
amplify publish
```

Amplify จะให้ URL เช่น: `https://xxxxx.amplifyapp.com`

## 🎯 ทางเลือกอื่น: Deploy Frontend บน S3 + CloudFront

### 3.5 (Alternative) Deploy ด้วย S3

```bash
cd frontend
npm run build

# สร้าง S3 bucket
aws s3 mb s3://buffet-ordering-frontend

# Upload files
aws s3 sync dist/ s3://buffet-ordering-frontend --acl public-read

# Enable website hosting
aws s3 website s3://buffet-ordering-frontend \
  --index-document index.html \
  --error-document index.html
```

URL: `http://buffet-ordering-frontend.s3-website-us-east-1.amazonaws.com`

### 3.6 (Optional) Setup CloudFront CDN

```bash
# สร้าง CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name buffet-ordering-frontend.s3.us-east-1.amazonaws.com \
  --default-root-object index.html
```

## 🔒 ส่วนที่ 4: Setup HTTPS (Optional แต่แนะนำ)

### 4.1 Register Domain (Route 53)

```bash
# ซื้อ domain จาก Route 53 หรือใช้ domain ที่มีอยู่
```

### 4.2 Request SSL Certificate (ACM)

```bash
# Request certificate
aws acm request-certificate \
  --domain-name yourdomain.com \
  --validation-method DNS
```

### 4.3 Update CloudFront ให้ใช้ HTTPS

```bash
# Update distribution to use SSL
aws cloudfront update-distribution \
  --id YOUR_DISTRIBUTION_ID \
  --viewer-certificate ACMCertificateArn=YOUR_CERT_ARN
```

## 📊 ส่วนที่ 5: Monitoring & Maintenance

### 5.1 Setup CloudWatch Alarms

```bash
# สร้าง alarm สำหรับ RDS
aws cloudwatch put-metric-alarm \
  --alarm-name buffet-db-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=buffet-db
```

### 5.2 ดู Logs

```bash
# Backend logs (Elastic Beanstalk)
eb logs

# หรือดูผ่าน CloudWatch
aws logs tail /aws/elasticbeanstalk/buffet-backend-env/var/log/web.stdout.log
```

### 5.3 Update Application

```bash
# Update backend
cd backend
eb deploy

# Update frontend (Amplify)
cd ../frontend
npm run build
amplify publish

# Update frontend (S3)
aws s3 sync dist/ s3://buffet-ordering-frontend --acl public-read
```

## 💰 การประเมินค่าใช้จ่าย (โดยประมาณ)

### Free Tier (12 เดือนแรก)
- EC2 t3.micro: 750 ชั่วโมง/เดือน (ฟรี)
- RDS t3.micro: 750 ชั่วโมง/เดือน (ฟรี)
- S3: 5GB storage (ฟรี)

### หลังจาก Free Tier
- Elastic Beanstalk (t3.small): ~$15/เดือน
- RDS (t3.micro): ~$15/เดือน
- S3 + CloudFront: ~$1-5/เดือน
- **รวม: ~$31-35/เดือน**

## 🛠️ Troubleshooting

### Backend ไม่ทำงาน

```bash
# ดู logs
eb logs

# SSH เข้า instance
eb ssh

# ตรวจสอบ environment variables
eb printenv
```

### Database connection error

```bash
# ตรวจสอบ security group
aws ec2 describe-security-groups --group-ids sg-xxxxx

# ทดสอบ connection
telnet buffet-db.xxxxx.us-east-1.rds.amazonaws.com 5432
```

### Frontend ไม่เชื่อมต่อ Backend

1. ตรวจสอบ CORS settings ใน backend
2. ตรวจสอบ `VITE_API_URL` ใน frontend
3. ตรวจสอบ Security Group ของ Elastic Beanstalk

## 🗑️ Clean Up (ลบทรัพยากรทั้งหมด)

```bash
# ลบ Elastic Beanstalk
eb terminate buffet-backend-env

# ลบ RDS
aws rds delete-db-instance \
  --db-instance-identifier buffet-db \
  --skip-final-snapshot

# ลบ S3
aws s3 rb s3://buffet-ordering-frontend --force

# ลบ Amplify
amplify delete
```

## 📞 Support

หากมีปัญหาติดต่อ:
- Email: your@email.com
- GitHub Issues: https://github.com/somchx/buffet-ordering-system/issues

---

## 🎉 สรุป URLs ที่ได้

เมื่อ deploy เสร็จจะได้:

1. **Backend API**: `http://buffet-backend-env.xxxxx.elasticbeanstalk.com`
   - API Docs: `http://buffet-backend-env.xxxxx.elasticbeanstalk.com/docs`

2. **Frontend Web**: `https://xxxxx.amplifyapp.com`
   หรือ `http://buffet-ordering-frontend.s3-website-us-east-1.amazonaws.com`

3. **Database**: `buffet-db.xxxxx.us-east-1.rds.amazonaws.com:5432`

สามารถเริ่มใช้งานได้ทันที! 🚀
