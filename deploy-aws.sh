#!/bin/bash

echo "🔄 Deploying to AWS..."
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   brew install awscli  # macOS"
    echo "   https://aws.amazon.com/cli/"
    exit 1
fi

# Check if configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run:"
    echo "   aws configure"
    exit 1
fi

echo "📦 Step 1: Deploying Backend to Elastic Beanstalk..."
cd backend

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "Installing EB CLI..."
    pip install awsebcli
fi

# Check if EB is initialized
if [ ! -d ".elasticbeanstalk" ]; then
    echo "Initializing Elastic Beanstalk..."
    eb init -p python-3.11 buffet-backend --region us-east-1
fi

# Check if environment exists
if ! eb status buffet-backend-env &> /dev/null; then
    echo "Creating Elastic Beanstalk environment..."
    read -p "Enter your RDS Database URL (or press Enter to skip): " DB_URL
    if [ -z "$DB_URL" ]; then
        eb create buffet-backend-env --instance-type t3.small
    else
        eb create buffet-backend-env --instance-type t3.small --envvars DATABASE_URL="$DB_URL"
    fi
else
    echo "Deploying to existing environment..."
    eb deploy
fi

echo ""
echo "✅ Backend deployed successfully!"
BACKEND_URL=$(eb status | grep "CNAME" | awk '{print $2}')
echo "Backend URL: http://$BACKEND_URL"
echo ""

# Seed data
echo "🌱 Seeding sample menu data..."
curl -X POST "http://$BACKEND_URL/api/seed"

echo ""
echo "📦 Step 2: Deploying Frontend to AWS Amplify..."
cd ../frontend

# Update API URL
cat > .env << EOF
VITE_API_URL=http://$BACKEND_URL
EOF

# Build
echo "Building frontend..."
npm install
npm run build

# Check if Amplify CLI is installed
if ! command -v amplify &> /dev/null; then
    echo "Installing Amplify CLI..."
    npm install -g @aws-amplify/cli
fi

echo ""
echo "⚠️  Manual step required for Amplify:"
echo "1. Run: amplify init"
echo "2. Run: amplify add hosting"
echo "3. Run: amplify publish"
echo ""
echo "Or deploy to S3:"
echo "1. aws s3 mb s3://buffet-ordering-frontend"
echo "2. aws s3 sync dist/ s3://buffet-ordering-frontend --acl public-read"
echo "3. aws s3 website s3://buffet-ordering-frontend --index-document index.html"
echo ""

cd ..

echo "✅ Deployment completed!"
echo ""
echo "📋 Summary:"
echo "   Backend:  http://$BACKEND_URL"
echo "   API Docs: http://$BACKEND_URL/docs"
echo ""
echo "For detailed instructions, see: AWS_DEPLOYMENT.md"
