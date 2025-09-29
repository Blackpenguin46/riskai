@echo off
REM RiskAI Development Startup Script for Windows
REM Starts both frontend and backend in development mode

echo 🚀 Starting RiskAI Platform (Development Mode)
echo ================================================

REM Check if we're in the correct directory
if not exist "docker-compose.yml" (
    echo ❌ Error: docker-compose.yml not found. Please run this script from the RiskAI root directory.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Create required directories if they don't exist
echo 📁 Creating required directories...
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\vectordb" mkdir "backend\vectordb"
if not exist "backend\uploads" mkdir "backend\uploads"

REM Set environment variables
set BACKEND_PORT=8000
set FRONTEND_PORT=3000

echo 🔧 Building and starting services...

REM Stop any existing containers
docker-compose down

REM Build and start services in development mode
docker-compose up --build -d

REM Wait for services to start
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check backend health
echo 🔍 Checking backend health...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/health >temp_status.txt 2>nul
set /p backend_health=<temp_status.txt
del temp_status.txt >nul 2>&1

if "%backend_health%"=="200" (
    echo ✅ Backend is healthy (http://localhost:8000)
) else (
    echo ⚠️  Backend may still be starting up (http://localhost:8000)
)

REM Check frontend health
echo 🔍 Checking frontend health...
curl -s -o nul -w "%%{http_code}" http://localhost:3000 >temp_status.txt 2>nul
set /p frontend_health=<temp_status.txt
del temp_status.txt >nul 2>&1

if "%frontend_health%"=="200" (
    echo ✅ Frontend is healthy (http://localhost:3000)
) else (
    echo ⚠️  Frontend may still be starting up (http://localhost:3000)
)

echo.
echo 🎉 RiskAI Platform Started Successfully!
echo ================================================
echo 📊 Frontend (Web Interface): http://localhost:3000
echo 🔧 Backend API:              http://localhost:8000
echo 📖 API Documentation:        http://localhost:8000/docs
echo ❤️  Health Check:            http://localhost:8000/health
echo.
echo 🔬 Enterprise Assessment:    http://localhost:3000/research-demo
echo 📋 Assessment Questions:     http://localhost:8000/api/assessment/enterprise/questions
echo 📊 Demo Data:               http://localhost:8000/api/demo/sample-assessment
echo.
echo To view logs:
echo   docker-compose logs -f backend
echo   docker-compose logs -f frontend
echo.
echo To stop the platform:
echo   docker-compose down
echo.
echo Happy assessing! 🛡️
echo.
echo Press any key to continue...
pause >nul