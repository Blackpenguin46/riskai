#!/bin/bash

# RiskAI Development Startup Script
# Starts both frontend and backend in development mode

echo "🚀 Starting RiskAI Platform (Development Mode)"
echo "================================================"

# Check if we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this script from the RiskAI root directory."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Create required directories if they don't exist
echo "📁 Creating required directories..."
mkdir -p backend/data
mkdir -p backend/vectordb
mkdir -p backend/uploads

# Set environment variables
export BACKEND_PORT=8000
export FRONTEND_PORT=3000

echo "🔧 Building and starting services..."

# Stop any existing containers
docker-compose down

# Build and start services in development mode
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check backend health
echo "🔍 Checking backend health..."
backend_health=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")

if [ "$backend_health" = "200" ]; then
    echo "✅ Backend is healthy (http://localhost:8000)"
else
    echo "⚠️  Backend may still be starting up (http://localhost:8000)"
fi

# Check frontend health
echo "🔍 Checking frontend health..."
frontend_health=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")

if [ "$frontend_health" = "200" ]; then
    echo "✅ Frontend is healthy (http://localhost:3000)"
else
    echo "⚠️  Frontend may still be starting up (http://localhost:3000)"
fi

echo ""
echo "🎉 RiskAI Platform Started Successfully!"
echo "================================================"
echo "📊 Frontend (Web Interface): http://localhost:3000"
echo "🔧 Backend API:              http://localhost:8000"
echo "📖 API Documentation:        http://localhost:8000/docs"
echo "❤️  Health Check:            http://localhost:8000/health"
echo ""
echo "🔬 Enterprise Assessment:    http://localhost:3000/research-demo"
echo "📋 Assessment Questions:     http://localhost:8000/api/assessment/enterprise/questions"
echo "📊 Demo Data:               http://localhost:8000/api/demo/sample-assessment"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f backend"
echo "  docker-compose logs -f frontend"
echo ""
echo "To stop the platform:"
echo "  docker-compose down"
echo ""
echo "Happy assessing! 🛡️"