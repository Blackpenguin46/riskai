#!/usr/bin/env python3
"""
RiskAI Quick Start Script

Automatically sets up and starts RiskAI for immediate testing and development.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
import signal
import threading

class RiskAIStarter:
    """Quick start manager for RiskAI"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_process = None
        self.frontend_process = None
        self.processes = []
        
    def check_requirements(self):
        """Check if all requirements are met"""
        
        print("🔍 Checking requirements...")
        
        # Check Python
        python_version = sys.version_info
        if python_version < (3, 9):
            print("❌ Python 3.9+ required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js {result.stdout.strip()}")
            else:
                print("❌ Node.js not found")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found")
            return False
        
        # Check npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm {result.stdout.strip()}")
            else:
                print("❌ npm not found")
                return False
        except FileNotFoundError:
            print("❌ npm not found")
            return False
        
        return True
    
    def setup_backend(self):
        """Setup backend environment"""
        
        print("🔧 Setting up backend...")
        
        backend_dir = self.base_dir / "backend"
        venv_dir = backend_dir / "venv"
        
        # Create virtual environment if it doesn't exist
        if not venv_dir.exists():
            print("  Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        
        # Get Python executable path
        if os.name == 'nt':  # Windows
            python_exe = venv_dir / "Scripts" / "python.exe"
            pip_exe = venv_dir / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            python_exe = venv_dir / "bin" / "python"
            pip_exe = venv_dir / "bin" / "pip"
        
        # Install requirements with compatibility handling
        requirements_file = backend_dir / "requirements-minimal.txt"
        if requirements_file.exists():
            print("  Installing Python dependencies (minimal version)...")
            try:
                subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️  Some packages failed to install: {e}")
                print("  Installing essential packages only...")
                self._install_essential_packages(pip_exe)
        else:
            # Try fixed requirements
            requirements_file = backend_dir / "requirements-fixed.txt"
            if requirements_file.exists():
                print("  Installing Python dependencies (compatible version)...")
                try:
                    subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"  ⚠️  Some packages failed to install: {e}")
                    print("  Installing essential packages only...")
                    self._install_essential_packages(pip_exe)
            else:
                # Fallback to original requirements
                requirements_file = backend_dir / "requirements.txt"
                if requirements_file.exists():
                    print("  Installing Python dependencies...")
                    try:
                        subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"  ⚠️  Some packages failed to install: {e}")
                        print("  Installing essential packages only...")
                        self._install_essential_packages(pip_exe)
        
        # Create data directories
        data_dir = backend_dir / "data"
        vectordb_dir = backend_dir / "vectordb"
        database_dir = backend_dir / "database_data"
        
        for directory in [data_dir, vectordb_dir, database_dir]:
            directory.mkdir(exist_ok=True)
        
        print("✅ Backend setup complete")
        return python_exe
    
    def _install_essential_packages(self, pip_exe):
        """Install essential packages one by one"""
        
        essential_packages = [
            "fastapi==0.115.9",
            "uvicorn==0.34.2", 
            "pydantic==2.11.4",
            "requests==2.32.3",
            "numpy==2.2.5",
            "pandas==2.2.3",
            "sqlalchemy==2.0.40",
            "python-multipart==0.0.20",
            "python-dotenv==1.1.0",
            "aiofiles==24.1.0",
            "PyYAML==6.0.2",
            "click==8.2.0",
            "rich==14.0.0",
            "tqdm==4.67.1"
        ]
        
        for package in essential_packages:
            try:
                print(f"    Installing {package}...")
                subprocess.run([str(pip_exe), "install", package], check=True)
            except subprocess.CalledProcessError:
                print(f"    ⚠️  Failed to install {package}, continuing...")
        
        # Try to install AI packages (optional)
        ai_packages = [
            "transformers==4.51.3",
            "torch==2.7.0",
            "tokenizers==0.21.1",
            "huggingface-hub==0.31.2"
        ]
        
        for package in ai_packages:
            try:
                print(f"    Installing {package} (optional)...")
                subprocess.run([str(pip_exe), "install", package], check=True)
            except subprocess.CalledProcessError:
                print(f"    ⚠️  Failed to install {package}, AI features may be limited...")
    
    def setup_frontend(self):
        """Setup frontend environment"""
        
        print("🔧 Setting up frontend...")
        
        frontend_dir = self.base_dir / "frontend"
        
        # Install npm dependencies
        print("  Installing Node.js dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        print("✅ Frontend setup complete")
    
    def start_backend(self, python_exe):
        """Start backend server"""
        
        print("🚀 Starting backend server...")
        
        backend_dir = self.base_dir / "backend"
        
        # Set environment variables
        env = os.environ.copy()
        env["PYTHONPATH"] = str(backend_dir)
        env["DATABASE_DIR"] = str(backend_dir / "database_data")
        env["PDF_DATA_DIR"] = str(backend_dir / "data")
        env["DB_PERSIST_DIR"] = str(backend_dir / "vectordb")
        
        # Start backend process using FastAPI server
        api_script = backend_dir / "api.py"
        if api_script.exists():
            self.backend_process = subprocess.Popen(
                [str(python_exe), "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                cwd=backend_dir,
                env=env
            )
        else:
            # Fallback to main.py
            main_script = backend_dir / "main.py"
            if main_script.exists():
                self.backend_process = subprocess.Popen(
                    [str(python_exe), str(main_script)],
                    cwd=backend_dir,
                    env=env
                )
        
        self.processes.append(self.backend_process)
        print("✅ Backend server started on http://localhost:8000")
    
    def start_frontend(self):
        """Start frontend development server"""
        
        print("🚀 Starting frontend server...")
        
        frontend_dir = self.base_dir / "frontend"
        
        # Set environment variables
        env = os.environ.copy()
        env["NEXT_PUBLIC_API_URL"] = "http://localhost:8000"
        
        # Start frontend process
        self.frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            env=env
        )
        
        self.processes.append(self.frontend_process)
        print("✅ Frontend server started on http://localhost:3000")
    
    def wait_for_services(self):
        """Wait for services to be ready"""
        
        print("⏳ Waiting for services to start...")
        
        # Wait for backend
        import requests
        backend_ready = False
        for i in range(30):  # 30 seconds timeout
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    backend_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not backend_ready:
            print("⚠️  Backend may not be ready yet...")
        else:
            print("✅ Backend is ready")
        
        # Wait for frontend
        frontend_ready = False
        for i in range(30):  # 30 seconds timeout
            try:
                response = requests.get("http://localhost:3000", timeout=1)
                if response.status_code == 200:
                    frontend_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not frontend_ready:
            print("⚠️  Frontend may not be ready yet...")
        else:
            print("✅ Frontend is ready")
    
    def open_browser(self):
        """Open browser to the application"""
        
        print("🌐 Opening RiskAI in your browser...")
        
        # Wait a moment for services to fully start
        time.sleep(3)
        
        try:
            webbrowser.open("http://localhost:3000")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("Please open http://localhost:3000 in your browser manually")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        
        def signal_handler(signum, frame):
            print("\n🛑 Shutting down RiskAI...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup(self):
        """Clean up processes"""
        
        print("🧹 Cleaning up processes...")
        
        for process in self.processes:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ Cleanup complete")
    
    def run(self):
        """Main run method"""
        
        print("🚀 Starting RiskAI...")
        print("=" * 50)
        
        # Check requirements
        if not self.check_requirements():
            print("❌ Requirements not met. Please install required software.")
            return
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        try:
            # Setup backend
            python_exe = self.setup_backend()
            
            # Setup frontend
            self.setup_frontend()
            
            # Start services
            self.start_backend(python_exe)
            time.sleep(5)  # Give backend time to start
            
            self.start_frontend()
            time.sleep(5)  # Give frontend time to start
            
            # Wait for services to be ready
            self.wait_for_services()
            
            # Open browser
            self.open_browser()
            
            # Show status
            print("\n" + "=" * 50)
            print("🎉 RiskAI is now running!")
            print("📱 Frontend: http://localhost:3000")
            print("🔧 Backend API: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/docs")
            print("=" * 50)
            print("\nPress Ctrl+C to stop RiskAI")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
                    
                    # Check if processes are still running
                    if self.backend_process and self.backend_process.poll() is not None:
                        print("❌ Backend process stopped unexpectedly")
                        break
                    
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        print("❌ Frontend process stopped unexpectedly")
                        break
                        
            except KeyboardInterrupt:
                pass
            
        except Exception as e:
            print(f"❌ Error starting RiskAI: {e}")
            
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Start RiskAI for development and testing")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--backend-only", action="store_true", help="Start backend only")
    parser.add_argument("--frontend-only", action="store_true", help="Start frontend only")
    
    args = parser.parse_args()
    
    starter = RiskAIStarter()
    
    if args.backend_only:
        if not starter.check_requirements():
            return
        python_exe = starter.setup_backend()
        starter.start_backend(python_exe)
        print("Backend started on http://localhost:8000")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            starter.cleanup()
            
    elif args.frontend_only:
        if not starter.check_requirements():
            return
        starter.setup_frontend()
        starter.start_frontend()
        print("Frontend started on http://localhost:3000")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            starter.cleanup()
            
    else:
        if args.no_browser:
            starter.open_browser = lambda: None
        
        starter.run()

if __name__ == "__main__":
    main()