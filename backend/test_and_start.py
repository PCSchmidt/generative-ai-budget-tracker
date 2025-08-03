#!/usr/bin/env python3
"""
AI Budget Tracker Backend Test & Start Script
Tests imports and starts the FastAPI server
"""

import sys
import os

print("🚀 AI Budget Tracker Backend Test & Start")
print("=" * 50)

# Test imports
print("🧪 Testing imports...")
try:
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")
    sys.exit(1)

try:
    import uvicorn
    print(f"✅ Uvicorn {uvicorn.__version__}")
except ImportError as e:
    print(f"❌ Uvicorn import failed: {e}")
    sys.exit(1)

try:
    from jose import jwt
    print("✅ python-jose")
except ImportError as e:
    print(f"❌ python-jose import failed: {e}")
    sys.exit(1)

try:
    import bcrypt
    print("✅ bcrypt")
except ImportError as e:
    print(f"❌ bcrypt import failed: {e}")
    sys.exit(1)

# Test FastAPI app import
print("\n🧪 Testing FastAPI app import...")
try:
    from app.main import app
    print("✅ FastAPI app imported successfully")
except ImportError as e:
    print(f"❌ FastAPI app import failed: {e}")
    print("Make sure you're in the backend directory and app/main.py exists")
    sys.exit(1)

# Start the server
print("\n🚀 Starting FastAPI server...")
print("📖 API Documentation: http://localhost:8000/docs")
print("🏥 Health Check: http://localhost:8000/health")
print("🛑 Press Ctrl+C to stop the server")
print("-" * 50)

if __name__ == "__main__":
    # Set PYTHONPATH to current directory
    sys.path.insert(0, os.getcwd())
    
    # Start uvicorn server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["."],
        log_level="info"
    )
