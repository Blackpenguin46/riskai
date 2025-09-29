#!/bin/bash

# RiskAI Enhanced Platform - One Command Startup
# Research Paper Demonstration

echo "🚀 Starting RiskAI Enhanced Platform..."
echo "📊 Research Implementation: Mathematical Scoring + AI Bias Detection + Source Attribution"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check backend health
echo "🔍 Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done

# Check frontend health
echo "🔍 Checking frontend health..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start"
        docker-compose logs frontend
        exit 1
    fi
    sleep 2
done

echo ""
echo "🎉 RiskAI Enhanced Platform is now running!"
echo ""
echo "📱 Access Points:"
echo "   🔬 Research Demo: http://localhost:3000/research-demo"
echo "   🏠 Main Platform: http://localhost:3000"
echo "   🔧 API Docs: http://localhost:8000/docs"
echo "   ❤️  Health Check: http://localhost:8000/health"
echo ""
echo "🎯 Research Components:"
echo "   ✅ Mathematical Scoring with Transparency"
echo "   ✅ AI Bias Detection & Mitigation"
echo "   ✅ Framework Source Attribution"
echo "   ✅ Real-time Analysis & Visualization"
echo ""
echo "📊 Demo Features:"
echo "   • 120-Question Assessment Engine"
echo "   • 12 Security Domains with Weighted Scoring"
echo "   • Multi-dimensional Bias Analysis"
echo "   • Framework Attribution (NIST, ISO 27001, CIS)"
echo "   • Interactive Visualizations"
echo ""
echo "🛑 To stop: docker-compose down"
echo "📋 To view logs: docker-compose logs -f"
echo ""
echo "🎓 Ready for research paper demonstration!"