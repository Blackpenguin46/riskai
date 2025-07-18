@echo off
echo 🚀 Starting RiskAI Portable...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Setup backend
cd backend
echo 📦 Installing Python dependencies...
python -m pip install -r requirements.txt

echo 🔧 Starting backend server...
start /b python api.py

REM Setup frontend
cd ..\frontend
echo 📦 Installing Node.js dependencies...
call npm install

echo 🌐 Starting frontend server...
start /b npm run dev

echo ✅ RiskAI is starting up...
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:8000
echo.
echo Press any key to stop RiskAI
pause >nul

REM Stop processes (simplified)
taskkill /f /im python.exe /t >nul 2>&1
taskkill /f /im node.exe /t >nul 2>&1
