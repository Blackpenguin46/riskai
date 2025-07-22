@echo off
setlocal enabledelayedexpansion

:: RiskAI Docker Deployment Script for Windows
:: This script provides a simple way to deploy the RiskAI application with Docker on Windows

:: Default configuration
set FRONTEND_PORT=3000
set BACKEND_PORT=8000

echo =========================================
echo        RiskAI Deployment Tool
echo =========================================

:: Check if Docker is installed and running
docker info > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not running or not installed.
    echo Please start Docker Desktop and try again.
    exit /b 1
)

:: Check if docker-compose is available
docker-compose version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Warning: docker-compose not found as standalone command.
    echo Will try to use 'docker compose' instead.
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

:: Function to check if a port is in use
call :check_ports

:: Create required directories
echo Checking required directories...

if not exist "data" (
    echo Creating data directory for PDF documents
    mkdir data
    echo Note: You should add your PDF documents to the 'data' directory
)

if not exist "vectordb" (
    echo Creating vectordb directory for vector database
    mkdir vectordb
)

if not exist "backend\database_data" (
    echo Creating database_data directory for SQLite database
    mkdir backend\database_data
)

:: Check if any PDF files exist in the data directory
dir /b data\*.pdf > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Warning: No PDF files found in the data directory
    echo The RAG system needs PDF documents to function properly
    echo Please add PDF files to the 'data' directory before or after starting
)

:: Stop any existing containers
echo Stopping any existing RiskAI containers...
%COMPOSE_CMD% down

:: Build and start the containers
echo Starting RiskAI with Docker...
echo This may take a few minutes on first run

%COMPOSE_CMD% up --build -d

if %ERRORLEVEL% equ 0 (
    echo Waiting for services to be ready...
    
    :: Wait for backend to be healthy
    echo Waiting for backend service.
    set /a attempts=0
    :wait_backend
    curl -s http://localhost:%BACKEND_PORT%/health > nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Backend service is ready!
    ) else (
        set /a attempts+=1
        if !attempts! lss 30 (
            echo .
            timeout /t 2 > nul
            goto wait_backend
        ) else (
            echo Backend service did not become ready in time
            echo Check the logs for more information:
            echo %COMPOSE_CMD% logs backend
        )
    )
    
    :: Wait for frontend to be healthy
    echo Waiting for frontend service.
    set /a attempts=0
    :wait_frontend
    curl -s http://localhost:%FRONTEND_PORT%/api/health > nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Frontend service is ready!
    ) else (
        set /a attempts+=1
        if !attempts! lss 30 (
            echo .
            timeout /t 2 > nul
            goto wait_frontend
        ) else (
            echo Frontend service did not become ready in time
            echo Check the logs for more information:
            echo %COMPOSE_CMD% logs frontend
        )
    )
    
    echo RiskAI has been deployed successfully!
    echo Frontend: http://localhost:%FRONTEND_PORT%
    echo Backend API: http://localhost:%BACKEND_PORT%
    echo.
    echo To view logs:
    echo %COMPOSE_CMD% logs -f
    echo.
    echo To stop the services:
    echo %COMPOSE_CMD% down
) else (
    echo Failed to start RiskAI containers
    echo Check the error messages above for more information
    exit /b 1
)

goto :eof

:check_ports
echo Checking for port conflicts...

:: Check if frontend port is in use
netstat -ano | findstr ":%FRONTEND_PORT%" > nul
if %ERRORLEVEL% equ 0 (
    echo Warning: Port %FRONTEND_PORT% is already in use
    set frontend_in_use=true
) else (
    set frontend_in_use=false
)

:: Check if backend port is in use
netstat -ano | findstr ":%BACKEND_PORT%" > nul
if %ERRORLEVEL% equ 0 (
    echo Warning: Port %BACKEND_PORT% is already in use
    set backend_in_use=true
) else (
    set backend_in_use=false
)

if "%frontend_in_use%"=="true" (
    set /p new_frontend_port="Enter alternative port for frontend (default: 3001): "
    if "!new_frontend_port!"=="" set new_frontend_port=3001
    set FRONTEND_PORT=!new_frontend_port!
)

if "%backend_in_use%"=="true" (
    set /p new_backend_port="Enter alternative port for backend (default: 8001): "
    if "!new_backend_port!"=="" set new_backend_port=8001
    set BACKEND_PORT=!new_backend_port!
)

if "%frontend_in_use%"=="true" (
    echo Using alternative frontend port: %FRONTEND_PORT%
)

if "%backend_in_use%"=="true" (
    echo Using alternative backend port: %BACKEND_PORT%
)

goto :eof