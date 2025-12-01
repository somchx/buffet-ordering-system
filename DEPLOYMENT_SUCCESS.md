# 🎉 Buffet Ordering System - Deployed on AWS!

## ✅ Deployment Complete!

### 🌐 Live URLs

#### Frontend (S3 Static Website)
**URL**: http://buffet-ordering-frontend-2025.s3-website-ap-southeast-1.amazonaws.com

- Built with: React + Vite
- Hosting: AWS S3 Static Website
- Region: ap-southeast-1 (Singapore)
- Status: ✅ Online

#### Backend (Elastic Beanstalk)
**API URL**: http://buffet-backend-env.eba-7bxec8ms.ap-southeast-1.elasticbeanstalk.com

**API Documentation**: http://buffet-backend-env.eba-7bxec8ms.ap-southeast-1.elasticbeanstalk.com/docs

- Built with: FastAPI (Python 3.11)
- Hosting: AWS Elastic Beanstalk
- Region: ap-southeast-1 (Singapore)
- Instance: t3.micro
- Database: SQLite
- Status: ✅ Green Health

---

## 🧪 Test the System

### 1. Open Frontend
```bash
open http://buffet-ordering-frontend-2025.s3-website-ap-southeast-1.amazonaws.com
```

### 2. Test Backend API
```bash
# Health check
curl http://buffet-backend-env.eba-7bxec8ms.ap-southeast-1.elasticbeanstalk.com/

# Get menu
curl http://buffet-backend-env.eba-7bxec8ms.ap-southeast-1.elasticbeanstalk.com/api/menu

# Start order
curl -X POST http://buffet-backend-env.eba-7bxec8ms.ap-southeast-1.elasticbeanstalk.com/api/orders/start \
  -H "Content-Type: application/json" \
  -d '{"table_number": "A1"}'
```

---

## 📊 AWS Resources Created

### S3 Bucket
- **Name**: buffet-ordering-frontend-2025
- **Purpose**: Frontend static website hosting
- **Region**: ap-southeast-1
- **Access**: Public read

### Elastic Beanstalk
- **Application**: buffet-backend
- **Environment**: buffet-backend-env
- **Platform**: Python 3.11 on Amazon Linux 2023
- **Instance Type**: t3.micro
- **Auto Scaling**: Single instance

### IAM
- **User**: deploy-user
- **Region**: ap-southeast-1

---

## 💰 Cost Estimation

### With AWS Free Tier (First 12 months)
- **EC2 (t3.micro)**: FREE (750 hours/month)
- **S3**: FREE (5GB storage, 20k GET requests)
- **Data Transfer**: FREE (15GB/month)
- **Total**: ~$0-2/month

### After Free Tier
- **EC2 (t3.micro)**: ~$10/month
- **S3**: ~$0.50/month
- **Data Transfer**: ~$1-5/month
- **Total**: ~$12-16/month

---

## 🔄 Update Deployment

### Update Frontend
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://buffet-ordering-frontend-2025
```

### Update Backend
```bash
cd backend
./venv/bin/eb deploy
```

---

## 🛠️ Management Commands

### Check Backend Status
```bash
cd backend
./venv/bin/eb status
```

### View Backend Logs
```bash
cd backend
./venv/bin/eb logs
```

### SSH to Backend Instance
```bash
cd backend
./venv/bin/eb ssh
```

### Open Backend in Browser
```bash
cd backend
./venv/bin/eb open
```

---

## 🌍 DNS Setup (Optional)

If you want to use a custom domain:

1. **Register domain** (e.g., on Route 53)
2. **Create CloudFront distribution** for S3
3. **Add SSL certificate** (AWS Certificate Manager)
4. **Update DNS records** to point to CloudFront

---

## 🔒 Security Notes

### Current Setup (Development)
- ✅ S3 bucket is public (for static website)
- ✅ Backend has CORS enabled for all origins
- ⚠️ No authentication/authorization
- ⚠️ SQLite database (not suitable for production scale)

### For Production
- [ ] Restrict CORS to specific domain
- [ ] Add JWT authentication
- [ ] Use RDS (PostgreSQL) instead of SQLite
- [ ] Add CloudFront CDN for frontend
- [ ] Enable HTTPS with SSL certificate
- [ ] Add WAF (Web Application Firewall)
- [ ] Enable CloudWatch monitoring
- [ ] Set up auto-scaling

---

## 📝 Features

### ✅ Implemented
- 105-minute timer (1 hour 45 minutes)
- Real-time countdown
- Menu selection with images
- Order management
- Auto-close when time expires
- Manual checkout
- Beautiful gradient UI
- Responsive design
- Thai language support

### 🚀 Future Enhancements
- [ ] WebSocket for real-time updates
- [ ] Admin dashboard
- [ ] QR code for each table
- [ ] Receipt printing
- [ ] Sales reports
- [ ] Multiple language support
- [ ] Mobile app
- [ ] Payment integration

---

## 🐛 Troubleshooting

### Frontend not loading
1. Check S3 bucket policy
2. Verify files uploaded correctly: `aws s3 ls s3://buffet-ordering-frontend-2025/`
3. Check browser console for errors

### Backend errors
1. Check logs: `cd backend && ./venv/bin/eb logs`
2. Check health: `cd backend && ./venv/bin/eb status`
3. Verify environment variables

### CORS errors
- Make sure backend CORS allows the frontend domain
- Clear browser cache

---

## 🗑️ Cleanup (Delete All Resources)

**Warning**: This will delete everything!

```bash
# Delete Elastic Beanstalk
cd backend
./venv/bin/eb terminate buffet-backend-env

# Delete S3 bucket
aws s3 rb s3://buffet-ordering-frontend-2025 --force
```

---

## 📞 Support

- **GitHub**: https://github.com/somchx/buffet-ordering-system
- **Issues**: https://github.com/somchx/buffet-ordering-system/issues

---

## 🎉 Success!

Your Buffet Ordering System is now live on AWS!

**Frontend**: http://buffet-ordering-frontend-2025.s3-website-ap-southeast-1.amazonaws.com

**Backend**: http://buffet-backend-env.eba-7bxec8ms.ap-southeast-1.elasticbeanstalk.com

Enjoy! 🍽️

---

**Deployed on**: December 1, 2025  
**Region**: ap-southeast-1 (Singapore)  
**Status**: ✅ Production Ready
