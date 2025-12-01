#!/bin/bash

echo "🚀 Starting Buffet Ordering System..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start containers
echo "📦 Building and starting containers..."
docker-compose up -d

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Seed data
echo "🌱 Seeding sample menu data..."
curl -X POST http://localhost:8000/api/seed

echo ""
echo "✅ System is ready!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend:  http://localhost"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 To stop the system:"
echo "   docker-compose down"
echo ""
