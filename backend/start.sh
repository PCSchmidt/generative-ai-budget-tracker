#!/bin/bash
# FastAPI Backend Startup Script

set -euo pipefail

echo "🚀 Starting AI Budget Tracker Backend..."
echo "📂 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ensure SECRET_KEY is not default
if [[ "${SECRET_KEY:-your-secret-key-change-in-production}" == "your-secret-key-change-in-production" ]]; then
  echo "❌ SECRET_KEY is default or unset. Set SECRET_KEY env var before starting." >&2
  exit 1
fi

# Run database migrations (fail fast if unavailable)
if command -v alembic >/dev/null 2>&1; then
  echo "🗃️ Running Alembic migrations..."
  alembic upgrade head || { echo "❌ Alembic migration failed"; exit 1; }
  REV=$(alembic current 2>/dev/null | awk '{print $1}')
  echo "✅ DB at migration revision: ${REV}" || true
else
  echo "⚠️ Alembic not installed; skipping migrations (NOT RECOMMENDED)." >&2
fi

# Start the FastAPI server
echo "🌐 Starting uvicorn server at http://localhost:8000"
UVICORN_CMD=(uvicorn app.main:app --host 0.0.0.0 --port 8000)
# Production should not use --reload; enable if DEV_MODE=1
if [[ "${DEV_MODE:-0}" == "1" ]]; then
  UVICORN_CMD+=(--reload)
fi
"${UVICORN_CMD[@]}"

echo "✅ Server started successfully!"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
