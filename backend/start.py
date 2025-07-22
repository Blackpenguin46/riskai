#!/usr/bin/env python3
"""
Simple startup script for RiskAI backend
"""

import sys
import os
import uvicorn

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Start the RiskAI backend server"""
    print("Starting RiskAI Backend Server...")
    print("Current directory:", current_dir)
    print("Python path:", sys.path[0])
    
    try:
        # Initialize database
        from database.models import init_database
        print("Initializing database...")
        init_database()
        print("✓ Database initialized")
        
        # Start server
        print("Starting server on http://localhost:8000")
        print("API docs available at: http://localhost:8000/docs")
        
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
        
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Make sure you've installed the dependencies:")
        print("pip install -r requirements-minimal.txt")

if __name__ == "__main__":
    main()