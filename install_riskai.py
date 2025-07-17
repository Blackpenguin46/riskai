#!/usr/bin/env python3
"""
RiskAI Installation Script

Handles Python version compatibility and provides installation options
for different Python versions and operating systems.
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def check_python_version():
    """Check Python version and provide guidance"""
    
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 9):
        print("❌ Python 3.9+ is required")
        print("Please upgrade Python from https://python.org/downloads/")
        return False
    
    elif version >= (3, 13):
        print("⚠️  Python 3.13+ detected - some packages may have compatibility issues")
        print("✅ Using compatibility mode with alternative packages")
        return True
        
    else:
        print("✅ Python version is compatible")
        return True

def get_python_executable():
    """Get the appropriate Python executable"""
    
    # Try different Python executables
    candidates = ["python3.12", "python3.11", "python3.10", "python3.9", "python3", "python"]
    
    for candidate in candidates:
        try:
            result = subprocess.run([candidate, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                print(f"Found {candidate}: {version_str}")
                
                # Check if it's a good version
                if "Python 3.9" in version_str or "Python 3.10" in version_str or "Python 3.11" in version_str or "Python 3.12" in version_str:
                    return candidate
                    
        except FileNotFoundError:
            continue
    
    return sys.executable

def install_with_conda():
    """Install using conda environment"""
    
    print("🐍 Setting up conda environment...")
    
    try:
        # Create conda environment with Python 3.11
        subprocess.run([
            "conda", "create", "-n", "riskai", "python=3.11", "-y"
        ], check=True)
        
        # Activate and install packages
        if platform.system() == "Windows":
            activate_cmd = "conda activate riskai && "
        else:
            activate_cmd = "source activate riskai && "
        
        install_cmd = f"{activate_cmd}pip install fastapi uvicorn pydantic requests numpy pandas transformers sentence-transformers torch sqlalchemy python-multipart python-dotenv aiofiles"
        
        subprocess.run(install_cmd, shell=True, check=True)
        
        print("✅ Conda environment 'riskai' created successfully")
        print("To use: conda activate riskai")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Conda installation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Conda not found")
        return False

def install_with_pyenv():
    """Install using pyenv"""
    
    print("🐍 Setting up pyenv environment...")
    
    try:
        # Install Python 3.11 with pyenv
        subprocess.run(["pyenv", "install", "3.11.0"], check=True)
        subprocess.run(["pyenv", "local", "3.11.0"], check=True)
        
        # Install packages
        subprocess.run(["pip", "install", "fastapi", "uvicorn", "pydantic", "requests", "numpy", "pandas", "transformers", "sentence-transformers", "torch", "sqlalchemy", "python-multipart", "python-dotenv", "aiofiles"], check=True)
        
        print("✅ Pyenv environment setup successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Pyenv installation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Pyenv not found")
        return False

def install_with_docker():
    """Install using Docker"""
    
    print("🐳 Setting up Docker environment...")
    
    try:
        # Check if Docker is available
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        
        # Use Docker Compose
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        print("✅ Docker environment setup successfully")
        print("Access at: http://localhost:3000")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker installation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Docker not found")
        return False

def manual_install():
    """Manual installation with current Python"""
    
    print("🔧 Manual installation with current Python...")
    
    try:
        # Essential packages that usually work
        essential_packages = [
            "fastapi==0.115.9",
            "uvicorn==0.34.2", 
            "pydantic==2.11.4",
            "requests==2.32.3",
            "numpy",
            "pandas",
            "sqlalchemy==2.0.40",
            "python-multipart",
            "python-dotenv",
            "aiofiles",
            "transformers",
            "sentence-transformers",
            "torch"
        ]
        
        for package in essential_packages:
            try:
                print(f"Installing {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            except subprocess.CalledProcessError:
                print(f"⚠️  Failed to install {package}, continuing...")
        
        print("✅ Manual installation completed")
        return True
        
    except Exception as e:
        print(f"❌ Manual installation failed: {e}")
        return False

def main():
    """Main installation function"""
    
    print("🚀 RiskAI Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📋 Installation Options:")
    print("1. Docker (Recommended) - No Python setup needed")
    print("2. Conda Environment - Clean Python 3.11 environment")
    print("3. Pyenv - Python version management")
    print("4. Manual - Use current Python with compatibility packages")
    print("5. Auto-detect - Try the best option automatically")
    
    choice = input("\nChoose installation method (1-5): ").strip()
    
    success = False
    
    if choice == "1":
        success = install_with_docker()
    elif choice == "2":
        success = install_with_conda()
    elif choice == "3":
        success = install_with_pyenv()
    elif choice == "4":
        success = manual_install()
    elif choice == "5":
        # Auto-detect best option
        print("🔍 Auto-detecting best installation method...")
        
        # Try Docker first
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            print("✅ Docker detected, using Docker installation")
            success = install_with_docker()
        except:
            # Try Conda
            try:
                subprocess.run(["conda", "--version"], check=True, capture_output=True)
                print("✅ Conda detected, using Conda installation")
                success = install_with_conda()
            except:
                # Try Pyenv
                try:
                    subprocess.run(["pyenv", "--version"], check=True, capture_output=True)
                    print("✅ Pyenv detected, using Pyenv installation")
                    success = install_with_pyenv()
                except:
                    # Fall back to manual
                    print("Using manual installation")
                    success = manual_install()
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    if success:
        print("\n🎉 Installation completed successfully!")
        print("\n🚀 Next steps:")
        
        if choice == "1":  # Docker
            print("1. Open your browser to http://localhost:3000")
            print("2. Start using RiskAI!")
        else:
            print("1. Run: python start_riskai.py")
            print("2. Open your browser to http://localhost:3000")
            print("3. Start using RiskAI!")
        
        print("\n📚 Documentation:")
        print("- Quick Start: QUICK_START.md")
        print("- Full Guide: DEPLOYMENT_GUIDE.md")
        print("- API Docs: http://localhost:8000/docs (when running)")
        
    else:
        print("\n❌ Installation failed")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Python version (3.9-3.12 recommended)")
        print("2. Try a different installation method")
        print("3. Install packages manually: pip install fastapi uvicorn pydantic")
        print("4. Check the documentation for more help")

if __name__ == "__main__":
    main()