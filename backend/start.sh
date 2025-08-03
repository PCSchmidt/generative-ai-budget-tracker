#!/bin/bash
# FastAPI Backend Startup Script

echo "🚀 Starting AI Budget Tracker Backend..."
echo "📂 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the FastAPI server
echo "🌐 Starting uvicorn server at http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo "✅ Server started successfully!"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
