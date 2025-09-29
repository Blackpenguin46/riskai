#!/usr/bin/env python3
"""
RiskAI Simple Startup Script
Cross-platform Python script to start both frontend and backend
"""

import os
import sys
import subprocess
import time
import requests
import platform
from pathlib import Path

def print_header():
    print("🚀 Starting RiskAI Platform (Development Mode)")
    print("=" * 48)

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_directory():
    """Check if we're in the correct directory"""
    return Path('docker-compose.yml').exists()

def create_directories():
    """Create required directories"""
    print("📁 Creating required directories...")
    dirs = ['backend/data', 'backend/vectordb', 'backend/uploads']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def start_services():
    """Start Docker services"""
    print("🔧 Building and starting services...")
    
    # Stop existing containers
    subprocess.run(['docker-compose', 'down'], capture_output=True)
    
    # Build and start services
    result = subprocess.run(['docker-compose', 'up', '--build', '-d'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error starting services: {result.stderr}")
        return False
    
    return True

def check_service_health(url, service_name):
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} is healthy ({url})")
            return True
        else:
            print(f"⚠️  {service_name} returned status {response.status_code} ({url})")
            return False
    except requests.RequestException:
        print(f"⚠️  {service_name} may still be starting up ({url})")
        return False

def wait_for_services():
    """Wait for services to start and check health"""
    print("⏳ Waiting for services to initialize...")
    time.sleep(10)
    
    print("🔍 Checking service health...")
    backend_healthy = check_service_health("http://localhost:8000/health", "Backend")
    frontend_healthy = check_service_health("http://localhost:3000", "Frontend")
    
    return backend_healthy, frontend_healthy

def print_success_info():
    """Print success information"""
    print()
    print("🎉 RiskAI Platform Started Successfully!")
    print("=" * 48)
    print("📊 Frontend (Web Interface): http://localhost:3000")
    print("🔧 Backend API:              http://localhost:8000")
    print("📖 API Documentation:        http://localhost:8000/docs")
    print("❤️  Health Check:            http://localhost:8000/health")
    print()
    print("🔬 Enterprise Assessment:    http://localhost:3000/research-demo")
    print("📋 Assessment Questions:     http://localhost:8000/api/assessment/enterprise/questions")
    print("📊 Demo Data:               http://localhost:8000/api/demo/sample-assessment")
    print()
    print("To view logs:")
    print("  docker-compose logs -f backend")
    print("  docker-compose logs -f frontend")
    print()
    print("To stop the platform:")
    print("  docker-compose down")
    print()
    print("Happy assessing! 🛡️")

def main():
    """Main startup function"""
    print_header()
    
    # Check if we're in the correct directory
    if not check_directory():
        print("❌ Error: docker-compose.yml not found.")
        print("Please run this script from the RiskAI root directory.")
        sys.exit(1)
    
    # Check if Docker is running
    if not check_docker():
        print("❌ Error: Docker is not running.")
        print("Please start Docker Desktop and try again.")
        sys.exit(1)
    
    # Create required directories
    create_directories()
    
    # Start services
    if not start_services():
        print("❌ Failed to start services. Check Docker logs for details.")
        sys.exit(1)
    
    # Wait and check health
    backend_healthy, frontend_healthy = wait_for_services()
    
    # Print success information
    print_success_info()
    
    # Additional wait for Windows
    if platform.system() == "Windows":
        input("Press Enter to continue...")

if __name__ == "__main__":
    main()