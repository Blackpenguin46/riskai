#!/usr/bin/env python3
"""
Startup script for RiskAI Backend on Render
Ensures proper port binding for deployment
"""

import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting RiskAI Backend on port {port}")
    
    # Start the server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )