#!/bin/bash
# FastAPI Backend Startup Script

set -euo pipefail

echo "🚀 Starting AI Budget Tracker Backend..."
echo "📂 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Add current directory to Python path (handle unset PYTHONPATH safely)
# If PYTHONPATH is unset, don't reference it directly when -u is enabled
if [[ -z "${PYTHONPATH+x}" ]]; then
  export PYTHONPATH="$(pwd)"
else
  export PYTHONPATH="${PYTHONPATH}:$(pwd)"
fi

# Ensure SECRET_KEY is not default
if [[ "${SECRET_KEY:-your-secret-key-change-in-production}" == "your-secret-key-change-in-production" ]]; then
  echo "❌ SECRET_KEY is default or unset. Set SECRET_KEY env var before starting." >&2
  exit 1
fi

# Run database migrations (fail fast if unavailable)
if command -v alembic >/dev/null 2>&1; then
  echo "🗃️ Running Alembic migrations (with retry until DB is ready)..."
  set +e  # temporarily disable exit-on-error for retry loop
  ATTEMPTS=0
  # Allow up to ~5 minutes by default (60 * 5s)
  MAX_ATTEMPTS=${ALEMBIC_MAX_ATTEMPTS:-60}
  SLEEP_SECONDS=${ALEMBIC_RETRY_SLEEP:-5}
  while true; do
    ATTEMPTS=$((ATTEMPTS+1))
    alembic upgrade head
    STATUS=$?
    if [[ $STATUS -eq 0 ]]; then
      echo "✅ Alembic migrations applied."
      break
    fi
    if [[ $ATTEMPTS -ge $MAX_ATTEMPTS ]]; then
      echo "❌ Alembic migration failed after ${ATTEMPTS} attempts; giving up." >&2
      set -e
      exit 1
    fi
    echo "⏳ Alembic attempt ${ATTEMPTS} failed (status=${STATUS}); DB might not be ready. Retrying in ${SLEEP_SECONDS}s..."
    sleep "$SLEEP_SECONDS"
  done
  set -e
  REV=$(alembic current 2>/dev/null | awk '{print $1}')
  echo "✅ DB at migration revision: ${REV}" || true
else
  echo "⚠️ Alembic not installed; skipping migrations (NOT RECOMMENDED)." >&2
fi

# Start the FastAPI server
PORT="${PORT:-8000}"
echo "🌐 Starting uvicorn server at http://0.0.0.0:${PORT}"
UVICORN_CMD=(uvicorn app.main:app --host 0.0.0.0 --port "${PORT}")
# Production should not use --reload; enable if DEV_MODE=1
if [[ "${DEV_MODE:-0}" == "1" ]]; then
  UVICORN_CMD+=(--reload)
fi
"${UVICORN_CMD[@]}"

echo "✅ Server started successfully!"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
