#!/bin/bash

# RiskAI Research Demo - Quick Start (No Docker)
# For immediate research paper demonstration

echo "🚀 Starting RiskAI Research Demo..."
echo "📊 Research Implementation: Mathematical Scoring + AI Bias Detection + Source Attribution"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    echo "   Visit: https://python.org/"
    exit 1
fi

# Kill any existing processes on ports 3000 and 8000
echo "🛑 Stopping any existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start backend
echo "🔧 Starting backend..."
cd backend
python3 main_api.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm install --silent
NEXT_TELEMETRY_DISABLED=1 npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running!"
else
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 RiskAI Research Demo is now running!"
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
echo "🛑 To stop: Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "🎓 Ready for research paper demonstration!"
echo ""

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for user to stop
trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; rm -f .backend.pid .frontend.pid; echo "✅ Services stopped!"; exit 0' INT

# Keep script running
wait