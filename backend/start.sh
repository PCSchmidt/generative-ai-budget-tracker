#!/bin/bash
# FastAPI Backend Startup Script

set -euo pipefail

echo "🚀 Starting AI Budget Tracker Backend..."
echo "📂 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "🛠️  Shell options: -euo pipefail"

# Add current directory to Python path (handle unset PYTHONPATH under set -u)
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

# Basic runtime diagnostics (do NOT print secrets)
if [[ -n "${SECRET_KEY:-}" ]]; then
  echo "🔐 SECRET_KEY length: ${#SECRET_KEY}"
else
  echo "❗ SECRET_KEY is not set (will fail fast below)"
fi

# Ensure SECRET_KEY is not default
if [[ "${SECRET_KEY:-your-secret-key-change-in-production}" == "your-secret-key-change-in-production" ]]; then
  echo "❌ SECRET_KEY is default or unset. Set SECRET_KEY env var before starting." >&2
  exit 1
fi

# Run database migrations (fail fast if unavailable)
if command -v alembic >/dev/null 2>&1; then
  echo "🗃️ Running Alembic migrations..."
  alembic upgrade head || { echo "❌ Alembic migration failed"; exit 1; }
  # Capture current revision; tolerate failure in info command
  REV="$( (alembic current 2>/dev/null | awk '{print $1}') || true )"
  echo "✅ DB at migration revision: ${REV:-unknown}" || true
  echo "ℹ️  Note: PostgreSQL collation mismatch warnings may appear and are informational unless migrations fail."
else
  echo "⚠️ Alembic not installed; skipping migrations (NOT RECOMMENDED)." >&2
fi

# Start the FastAPI server
PORT="${PORT:-8000}"
UVICORN_LOG_LEVEL="${UVICORN_LOG_LEVEL:-info}"
echo "🌐 Starting uvicorn server at http://0.0.0.0:${PORT} (log-level=${UVICORN_LOG_LEVEL})"
UVICORN_CMD=(uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --log-level "${UVICORN_LOG_LEVEL}" --access-log)
# Production should not use --reload; enable if DEV_MODE=1
if [[ "${DEV_MODE:-0}" == "1" ]]; then
  UVICORN_CMD+=(--reload)
fi
"${UVICORN_CMD[@]}"

echo "✅ Server started successfully!"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
