#!/usr/bin/env python3
"""
FastAPI Application Startup Script

This script starts the FastAPI application using environment variables
for host and port configuration.
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting FastAPI server on {settings.fastapi_host}:{settings.fastapi_port}")
    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True
    ) 