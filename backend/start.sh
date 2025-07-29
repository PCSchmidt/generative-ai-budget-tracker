#!/bin/bash
# Railway startup script that handles PORT environment variable properly

# Set default port if PORT is not set or empty
PORT=${PORT:-8000}

# Validate PORT is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Warning: PORT '$PORT' is not a valid number, using default 8000"
    PORT=8000
fi

echo "Starting FastAPI server on port $PORT"
echo "Environment: $(env | grep -E '^(PORT|DATABASE_URL|DEBUG)=')"

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --access-log
