#!/usr/bin/env python3
"""
FastAPI Application Startup Script

This script starts the FastAPI application using environment variables
for host and port configuration.

Requirements:
- Use the app's virtual environment: source app/venv/bin/activate
- Run from backend directory with proper PYTHONPATH
"""

import uvicorn
import sys
import os

# Add necessary paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting FastAPI server on {settings.fastapi_host}:{settings.fastapi_port}")
    print(f"💡 Using environment: app virtual environment")
    print(f"📁 Working directory: {os.getcwd()}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True
    ) 