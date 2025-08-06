# Railway optimized Dockerfile for AI Budget Tracker - LIGHTWEIGHT VERSION
FROM python:3.11-slim

WORKDIR /app

# NO system dependencies needed for lightweight packages
# RUN apt-get update && apt-get install -y gcc  # REMOVED - causes 6GB bloat

# Copy and install LIGHTWEIGHT Python dependencies
COPY backend/requirements-light.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-light.txt

# Copy application code
COPY backend/app ./app

# Copy and make startup script executable
COPY backend/start.sh ./start.sh
RUN chmod +x ./start.sh

# Use startup script that handles PORT variable
CMD ["./start.sh"]
