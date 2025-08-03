#!/usr/bin/env python
"""
Simple startup script for FastAPI backend
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the FastAPI app
from app.main import app

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Budget Tracker Backend...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
