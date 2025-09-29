@echo off
REM RiskAI Enhanced Platform - One Command Startup (Windows)
REM Research Paper Demonstration

echo 🚀 Starting RiskAI Enhanced Platform...
echo 📊 Research Implementation: Mathematical Scoring + AI Bias Detection + Source Attribution
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo    Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    echo    Visit: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down --remove-orphans

REM Build and start containers
echo 🔨 Building and starting containers...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check backend health
echo 🔍 Checking backend health...
for /l %%i in (1,1,30) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Backend is ready!
        goto frontend_check
    )
    timeout /t 2 /nobreak >nul
)
echo ❌ Backend failed to start
docker-compose logs backend
pause
exit /b 1

:frontend_check
REM Check frontend health
echo 🔍 Checking frontend health...
for /l %%i in (1,1,30) do (
    curl -s http://localhost:3000 >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Frontend is ready!
        goto success
    )
    timeout /t 2 /nobreak >nul
)
echo ❌ Frontend failed to start
docker-compose logs frontend
pause
exit /b 1

:success
echo.
echo 🎉 RiskAI Enhanced Platform is now running!
echo.
echo 📱 Access Points:
echo    🔬 Research Demo: http://localhost:3000/research-demo
echo    🏠 Main Platform: http://localhost:3000
echo    🔧 API Docs: http://localhost:8000/docs
echo    ❤️  Health Check: http://localhost:8000/health
echo.
echo 🎯 Research Components:
echo    ✅ Mathematical Scoring with Transparency
echo    ✅ AI Bias Detection ^& Mitigation
echo    ✅ Framework Source Attribution
echo    ✅ Real-time Analysis ^& Visualization
echo.
echo 📊 Demo Features:
echo    • 120-Question Assessment Engine
echo    • 12 Security Domains with Weighted Scoring
echo    • Multi-dimensional Bias Analysis
echo    • Framework Attribution (NIST, ISO 27001, CIS)
echo    • Interactive Visualizations
echo.
echo 🛑 To stop: docker-compose down
echo 📋 To view logs: docker-compose logs -f
echo.
echo 🎓 Ready for research paper demonstration!
echo.
pause