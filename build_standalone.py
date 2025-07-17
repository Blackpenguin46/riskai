#!/usr/bin/env python3
"""
Standalone Distribution Builder for RiskAI

Creates a standalone executable package that bundles Python backend,
React frontend, and all dependencies for easy distribution to non-technical users.
"""

import os
import sys
import shutil
import subprocess
import platform
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

class StandaloneBuilder:
    """Build standalone distribution packages"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.build_dir = self.base_dir / "dist"
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()
        
        # Build configuration
        self.config = {
            "app_name": "RiskAI",
            "version": "2.0.0",
            "description": "AI-Powered Risk Assessment Platform",
            "author": "RiskAI Team",
            "backend_port": 8000,
            "frontend_port": 3000,
            "database_dir": "data",
            "log_dir": "logs"
        }
        
        print(f"Building for {self.platform} {self.arch}")
        
    def build_all(self):
        """Build complete standalone package"""
        
        print("Starting standalone build process...")
        
        # Clean previous builds
        self.clean_build_dir()
        
        # Build backend
        print("Building backend...")
        self.build_backend()
        
        # Build frontend
        print("Building frontend...")
        self.build_frontend()
        
        # Create runtime scripts
        print("Creating runtime scripts...")
        self.create_runtime_scripts()
        
        # Package everything
        print("Creating installer package...")
        self.create_installer()
        
        print(f"Standalone build completed! Package location: {self.build_dir}")
        
    def clean_build_dir(self):
        """Clean the build directory"""
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
    def build_backend(self):
        """Build backend using PyInstaller"""
        
        backend_dir = self.build_dir / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        # Create main backend script
        main_script = self.create_backend_main()
        
        # Build with PyInstaller
        pyinstaller_args = [
            "pyinstaller",
            "--onefile",
            "--windowed" if self.platform == "windows" else "",
            "--name", f"riskai-backend",
            "--distpath", str(backend_dir),
            "--workpath", str(self.build_dir / "temp"),
            "--specpath", str(self.build_dir / "temp"),
            "--add-data", f"{self.base_dir}/backend/data;data",
            "--add-data", f"{self.base_dir}/backend/vectordb;vectordb",
            "--hidden-import", "sklearn",
            "--hidden-import", "transformers",
            "--hidden-import", "torch",
            "--hidden-import", "chromadb",
            str(main_script)
        ]
        
        # Filter out empty strings
        pyinstaller_args = [arg for arg in pyinstaller_args if arg]
        
        try:
            subprocess.run(pyinstaller_args, check=True, cwd=self.base_dir)
            print("Backend built successfully")
        except subprocess.CalledProcessError as e:
            print(f"Backend build failed: {e}")
            sys.exit(1)
            
    def create_backend_main(self) -> Path:
        """Create main backend script for PyInstaller"""
        
        main_script = self.build_dir / "temp" / "main_backend.py"
        main_script.parent.mkdir(parents=True, exist_ok=True)
        
        script_content = '''
import sys
import os
import multiprocessing
from pathlib import Path

# Add the backend directory to Python path
if hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    base_path = Path(sys._MEIPASS)
else:
    # Running in development
    base_path = Path(__file__).parent

sys.path.insert(0, str(base_path))

# Set environment variables
os.environ['DATABASE_DIR'] = str(base_path / 'data')
os.environ['PDF_DATA_DIR'] = str(base_path / 'data')
os.environ['DB_PERSIST_DIR'] = str(base_path / 'vectordb')

def main():
    """Main entry point for backend"""
    
    # Create data directories
    data_dir = base_path / 'data'
    data_dir.mkdir(exist_ok=True)
    
    vectordb_dir = base_path / 'vectordb'
    vectordb_dir.mkdir(exist_ok=True)
    
    # Import and run the backend
    try:
        from backend.api import app
        import uvicorn
        
        print("Starting RiskAI Backend...")
        print(f"Data directory: {data_dir}")
        print(f"Vector database: {vectordb_dir}")
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=False
        )
        
    except Exception as e:
        print(f"Error starting backend: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
'''
        
        with open(main_script, 'w') as f:
            f.write(script_content)
            
        return main_script
        
    def build_frontend(self):
        """Build frontend using Node.js"""
        
        frontend_dir = self.base_dir / "frontend"
        build_output = self.build_dir / "frontend"
        
        # Install dependencies
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("Frontend dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"Frontend dependency installation failed: {e}")
            sys.exit(1)
            
        # Build production version
        try:
            env = os.environ.copy()
            env["NEXT_PUBLIC_API_URL"] = "http://localhost:8000"
            
            subprocess.run(["npm", "run", "build"], cwd=frontend_dir, env=env, check=True)
            print("Frontend built successfully")
            
            # Copy build output
            if (frontend_dir / "out").exists():
                shutil.copytree(frontend_dir / "out", build_output)
            elif (frontend_dir / ".next").exists():
                shutil.copytree(frontend_dir / ".next", build_output / ".next")
                shutil.copytree(frontend_dir / "public", build_output / "public")
                
        except subprocess.CalledProcessError as e:
            print(f"Frontend build failed: {e}")
            sys.exit(1)
            
    def create_runtime_scripts(self):
        """Create runtime scripts for different platforms"""
        
        if self.platform == "windows":
            self.create_windows_scripts()
        else:
            self.create_unix_scripts()
            
    def create_windows_scripts(self):
        """Create Windows batch scripts"""
        
        # Main launcher script
        launcher_script = self.build_dir / "RiskAI.bat"
        launcher_content = f'''@echo off
echo Starting RiskAI...
echo.

REM Create data directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Start backend
echo Starting backend server...
start "RiskAI Backend" /min backend\\riskai-backend.exe

REM Wait for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend (using built-in simple server)
echo Starting frontend...
start "RiskAI Frontend" /min python -m http.server 3000 --directory frontend

REM Wait for frontend to start
timeout /t 3 /nobreak >nul

REM Open browser
echo Opening RiskAI in your browser...
start http://localhost:3000

echo.
echo RiskAI is now running!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop RiskAI...
pause >nul

REM Stop services
taskkill /f /im riskai-backend.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1

echo RiskAI stopped.
'''
        
        with open(launcher_script, 'w') as f:
            f.write(launcher_content)
            
        # Stop script
        stop_script = self.build_dir / "Stop-RiskAI.bat"
        stop_content = '''@echo off
echo Stopping RiskAI...
taskkill /f /im riskai-backend.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
echo RiskAI stopped.
pause
'''
        
        with open(stop_script, 'w') as f:
            f.write(stop_content)
            
    def create_unix_scripts(self):
        """Create Unix shell scripts"""
        
        # Main launcher script
        launcher_script = self.build_dir / "riskai.sh"
        launcher_content = f'''#!/bin/bash

echo "Starting RiskAI..."
echo

# Create data directories
mkdir -p data logs

# Function to cleanup on exit
cleanup() {{
    echo "Stopping RiskAI..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend server..."
./backend/riskai-backend &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

# Open browser (Linux/macOS)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    open http://localhost:3000
fi

echo
echo "RiskAI is now running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo
echo "Press Ctrl+C to stop RiskAI..."

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
'''
        
        with open(launcher_script, 'w') as f:
            f.write(launcher_content)
            
        # Make executable
        os.chmod(launcher_script, 0o755)
        
        # Stop script
        stop_script = self.build_dir / "stop-riskai.sh"
        stop_content = '''#!/bin/bash
echo "Stopping RiskAI..."
pkill -f riskai-backend
pkill -f "python.*http.server.*3000"
echo "RiskAI stopped."
'''
        
        with open(stop_script, 'w') as f:
            f.write(stop_content)
            
        os.chmod(stop_script, 0o755)
        
    def create_installer(self):
        """Create installer package"""
        
        # Create README
        readme_content = f'''# RiskAI Standalone Distribution

## Installation Instructions

### Windows
1. Extract the zip file to a folder (e.g., C:\\RiskAI)
2. Double-click "RiskAI.bat" to start the application
3. The application will open in your web browser automatically

### Linux/macOS
1. Extract the tar.gz file to a folder (e.g., ~/RiskAI)
2. Open terminal and navigate to the folder
3. Run: ./riskai.sh
4. The application will open in your web browser automatically

## Usage

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Data Storage**: All data is stored locally in the 'data' folder

## Features

- Complete risk assessment platform
- AI-powered analysis and recommendations
- Industry benchmarking and comparisons
- Persistent data storage
- No internet connection required (after installation)

## System Requirements

- **Windows**: Windows 10 or later
- **Linux**: Ubuntu 18.04+ or equivalent
- **macOS**: macOS 10.14+ 
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Browser**: Chrome, Firefox, Safari, or Edge

## Troubleshooting

1. **Port conflicts**: If ports 3000 or 8000 are in use, modify the scripts
2. **Permission issues**: Run as administrator (Windows) or use sudo (Linux/macOS)
3. **Browser doesn't open**: Manually navigate to http://localhost:3000

## Support

For support, please visit: https://github.com/riskai/riskai

## Version Information

- Version: {self.config['version']}
- Build Date: {self.get_build_date()}
- Platform: {self.platform} {self.arch}
'''
        
        readme_file = self.build_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
            
        # Create version info
        version_info = {
            "version": self.config['version'],
            "build_date": self.get_build_date(),
            "platform": self.platform,
            "architecture": self.arch,
            "components": {
                "backend": "Python + FastAPI",
                "frontend": "React + Next.js",
                "database": "SQLite",
                "ai_engine": "HuggingFace Transformers"
            }
        }
        
        version_file = self.build_dir / "version.json"
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
            
        # Create archive
        archive_name = f"riskai-{self.config['version']}-{self.platform}-{self.arch}"
        
        if self.platform == "windows":
            shutil.make_archive(
                str(self.build_dir.parent / archive_name),
                'zip',
                str(self.build_dir)
            )
        else:
            shutil.make_archive(
                str(self.build_dir.parent / archive_name),
                'gztar',
                str(self.build_dir)
            )
            
        print(f"Installer package created: {archive_name}")
        
    def get_build_date(self) -> str:
        """Get current build date"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def install_dependencies(self):
        """Install required build dependencies"""
        
        print("Installing build dependencies...")
        
        # Python dependencies
        python_deps = [
            "pyinstaller",
            "auto-py-to-exe",  # Optional GUI for PyInstaller
        ]
        
        for dep in python_deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print(f"Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {dep}")
                
        # Check Node.js
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            print("Node.js and npm are available")
        except subprocess.CalledProcessError:
            print("Error: Node.js and npm are required for building frontend")
            print("Please install Node.js from https://nodejs.org/")
            sys.exit(1)

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Build RiskAI standalone distribution")
    parser.add_argument("--install-deps", action="store_true", help="Install build dependencies")
    parser.add_argument("--base-dir", help="Base directory for build")
    parser.add_argument("--clean", action="store_true", help="Clean build directory only")
    
    args = parser.parse_args()
    
    builder = StandaloneBuilder(args.base_dir)
    
    if args.install_deps:
        builder.install_dependencies()
        return
        
    if args.clean:
        builder.clean_build_dir()
        print("Build directory cleaned")
        return
        
    builder.build_all()

if __name__ == "__main__":
    main()