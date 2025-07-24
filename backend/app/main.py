"""
AI Budget Tracker - Minimal FastAPI for Railway Deployment
Starting simple like Journal Summarizer, will add complexity later
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Create FastAPI application
app = FastAPI(
    title="AI Budget Tracker API",
    description="Smart expense tracking (minimal deployment version)",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - Railway health check"""
    return {
        "message": "🚀 AI Budget Tracker API is running on Railway!",
        "version": "1.0.0-minimal",
        "status": "healthy",
        "deployment": "railway",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "note": "Minimal deployment - AI features coming soon!"
    }

@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy", "service": "ai-budget-tracker-minimal"}

@app.get("/api/expenses")
async def get_expenses():
    """Demo expenses endpoint"""
    return {
        "expenses": [
            {"id": 1, "amount": 12.50, "description": "Coffee", "category": "Food"},
            {"id": 2, "amount": 45.00, "description": "Gas", "category": "Transport"},
            {"id": 3, "amount": 89.99, "description": "Groceries", "category": "Food"}
        ],
        "total": 3,
        "total_amount": 147.49,
        "mode": "demo"
    }

@app.post("/api/expenses")
async def create_expense():
    """Demo create expense"""
    return {
        "message": "Expense endpoint ready",
        "id": 999,
        "status": "demo_mode"
    }

@app.get("/api/insights")
async def get_insights():
    """Demo financial insights"""
    return {
        "insights": {
            "advice": "You're spending most on Food & Dining. Consider setting a weekly food budget!",
            "top_category": "Food & Dining",
            "total_tracked": 147.49
        },
        "mode": "demo",
        "ai_status": "coming_soon"
    }

# Start the application (Railway deployment pattern)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
