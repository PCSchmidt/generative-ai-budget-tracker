#!/usr/bin/env python
"""
Test script to verify all dependencies are available
"""
import sys
import os

print("🧪 Testing FastAPI Backend Dependencies...")
print(f"📍 Current directory: {os.getcwd()}")
print(f"🐍 Python version: {sys.version}")

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    print("✅ Testing FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    print("✅ Testing python-jose...")
    from jose import jwt
    print("✅ python-jose imported successfully")
except ImportError as e:
    print(f"❌ python-jose import failed: {e}")

try:
    print("✅ Testing bcrypt...")
    import bcrypt
    print("✅ bcrypt imported successfully")
except ImportError as e:
    print(f"❌ bcrypt import failed: {e}")

try:
    print("✅ Testing pydantic...")
    from pydantic import BaseModel
    print("✅ pydantic imported successfully")
except ImportError as e:
    print(f"❌ pydantic import failed: {e}")

try:
    print("✅ Testing app.main...")
    import app.main
    print("✅ app.main imported successfully")
    print(f"✅ FastAPI app found: {hasattr(app.main, 'app')}")
except ImportError as e:
    print(f"❌ app.main import failed: {e}")

print("\n🎯 Dependency test complete!")
