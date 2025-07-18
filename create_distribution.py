#!/usr/bin/env python3
"""
Create Distribution Package for RiskAI

Creates a portable version of RiskAI that can be easily shared and run
on different machines without complex installation.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
import platform

def create_portable_distribution():
    """Create a portable distribution of RiskAI"""
    
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "riskai_portable"
    
    print("🚀 Creating RiskAI Portable Distribution...")
    
    # Clean and create distribution directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copy essential backend files
    backend_dist = dist_dir / "backend"
    backend_dist.mkdir()
    
    # Copy core backend modules
    essential_dirs = [
        "api.py",
        "assessment/",
        "scoring/", 
        "database/",
        "rag_pipeline/",
        "validation/",
        "benchmarks/",
        "data_pipeline/",
        "analytics/",
        "chat/",
        "dashboard/",
        "llm/",
        "metrics/",
        "data_management/",
        "session_manager.py",
        "start.py",
        "main.py"
    ]
    
    for item in essential_dirs:
        src = base_dir / "backend" / item
        dst = backend_dist / item
        
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            else:
                shutil.copy2(src, dst)
    
    # Copy minimal requirements
    shutil.copy2(base_dir / "backend" / "requirements-minimal.txt", backend_dist / "requirements.txt")
    
    # Copy frontend
    frontend_src = base_dir / "frontend"
    frontend_dist = dist_dir / "frontend"
    
    if frontend_src.exists():
        print("📦 Copying frontend...")
        shutil.copytree(
            frontend_src, 
            frontend_dist, 
            ignore=shutil.ignore_patterns('node_modules', '.next', 'build', '*.log')
        )
    
    # Copy data files (smaller subset)
    data_src = base_dir / "backend" / "data"
    data_dist = backend_dist / "data"
    data_dist.mkdir()
    
    # Copy essential data files only
    essential_files = [
        "NIST.SP.800-37r2.pdf",
        "Risk_Management_Governance_v1.1.1.pdf",
        "cybersecurity-risk-management-standard-v1.pdf",
        "CyBOK_v1.1.0.pdf"
    ]
    
    for filename in essential_files:
        src_file = data_src / filename
        if src_file.exists():
            shutil.copy2(src_file, data_dist / filename)
    
    # Create startup scripts
    create_startup_scripts(dist_dir)
    
    # Create README
    create_readme(dist_dir)
    
    # Create ZIP archive
    print("📁 Creating ZIP archive...")
    zip_path = base_dir / f"riskai_portable_{platform.system().lower()}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Distribution created: {zip_path}")
    print(f"📁 Portable folder: {dist_dir}")
    
    return zip_path

def create_startup_scripts(dist_dir):
    """Create platform-specific startup scripts"""
    
    # Unix/Linux/macOS script
    unix_script = dist_dir / "start_riskai.sh"
    unix_content = '''#!/bin/bash
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
'''
    
    with open(unix_script, 'w') as f:
        f.write(unix_content)
    unix_script.chmod(0o755)
    
    # Windows script
    windows_script = dist_dir / "start_riskai.bat"
    windows_content = '''@echo off
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
cd ..\\frontend
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
'''
    
    with open(windows_script, 'w') as f:
        f.write(windows_content)

def create_readme(dist_dir):
    """Create README file"""
    
    readme_content = '''# RiskAI Portable Distribution

## Quick Start

### Prerequisites
- Python 3.9+ (https://python.org)
- Node.js 16+ (https://nodejs.org)

### Running RiskAI

**On macOS/Linux:**
```bash
./start_riskai.sh
```

**On Windows:**
```cmd
start_riskai.bat
```

### Manual Setup

1. **Backend Setup:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python api.py
   ```

2. **Frontend Setup (in new terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the Application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Features

- ✅ AI-powered risk assessment
- ✅ Industry benchmarking 
- ✅ Quantitative and qualitative scoring
- ✅ Session persistence
- ✅ Enterprise GRC comparison
- ✅ Python 3.13 compatibility

## Enterprise Distribution

This portable version is designed for:
- Non-technical decision makers
- Corporate environments
- Air-gapped networks
- Quick demos and evaluations

## Support

For issues or questions, please visit:
https://github.com/Blackpenguin46/riskai

---
Generated with RiskAI Distribution Builder
'''
    
    readme_file = dist_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)

if __name__ == "__main__":
    create_portable_distribution()