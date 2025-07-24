# Railway optimized Dockerfile for AI Budget Tracker
FROM python:3.11-slim

WORKDIR /app

# Railway best practice - minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app

# Copy and make startup script executable
COPY backend/start.sh ./start.sh
RUN chmod +x ./start.sh

# Use startup script that handles PORT variable
CMD ["./start.sh"]
