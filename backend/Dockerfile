# AI Budget Tracker Backend - Railway Deployment
# Based on successful Journal Summarizer patterns

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for Railway
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Copy application code
COPY app ./app

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Start command for Railway (use shell for proper PORT variable expansion)
CMD ["sh", "-c", "uvicorn app.main_light:app --host 0.0.0.0 --port ${PORT:-8000}"]
