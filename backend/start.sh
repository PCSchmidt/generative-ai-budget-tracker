#!/bin/bash
# FastAPI Backend Startup Script

set -euo pipefail

echo "🚀 Starting AI Budget Tracker Backend..."
echo "📂 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "🛠️  Shell options: -euo pipefail"

# Add current directory and ./app to Python path (handle unset under set -u)
export PYTHONPATH="${PYTHONPATH:-}:$(pwd):$(pwd)/app"

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

# Preflight diagnostics: ensure module import path is sane
echo "📁 Directory listing (root):"
ls -la || true
echo "📁 Directory listing (./app):"
ls -la app || true
echo "🧪 Import check: app.main (package import)"
python - <<'PY'
import sys, traceback, importlib
print('sys.path=', sys.path)
try:
  # Ensure ./app is on path for package imports
  if '/app/app' not in sys.path:
    sys.path.insert(0, '/app/app')
  importlib.import_module('app.main')
  print('import app.main: OK')
except Exception as e:
  print('import app.main: WARN:', e)
  traceback.print_exc()
  # Do not raise; continue to let uvicorn handle app loading
PY

# Quick sanity check for app entrypoint
if [[ ! -f "app/main.py" ]]; then
  echo "❌ app/main.py not found. Listing app directory again for diagnostics:" >&2
  ls -la app || true
fi

# Start uvicorn against the package module path (app.main:app)
UVICORN_CMD=(uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --log-level "${UVICORN_LOG_LEVEL}" --access-log)
# Production should not use --reload; enable if DEV_MODE=1
if [[ "${DEV_MODE:-0}" == "1" ]]; then
  UVICORN_CMD+=(--reload)
fi
"${UVICORN_CMD[@]}"

echo "✅ Server started successfully!"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
