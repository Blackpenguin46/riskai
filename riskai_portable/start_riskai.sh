#!/bin/bash
echo "🚀 Starting RiskAI Portable..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js from https://nodejs.org"
    exit 1
fi

# Setup backend
cd backend
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo "🔧 Starting backend server..."
python3 api.py &
BACKEND_PID=$!

# Setup frontend
cd ../frontend
echo "📦 Installing Node.js dependencies..."
npm install

echo "🌐 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo "✅ RiskAI is starting up..."
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop RiskAI"

# Wait for user interrupt
trap "echo 'Stopping RiskAI...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
