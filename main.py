# main.py - FastAPI main application for local development
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import asyncio
import logging

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import our modules
import ai_categorizer
from database_service import DatabaseService
from analytics_engine import AnalyticsEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Budget Tracker v3.0",
    description="Advanced AI-powered budget tracking with spending analytics",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db_service = None
analytics_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global db_service, analytics_engine
    
    logger.info("🚀 Starting AI Budget Tracker v3.0")
    
    # Initialize database service
    try:
        db_service = DatabaseService()
        logger.info("✅ Database service initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database service not available: {e}")
        db_service = None
    
    # Initialize analytics engine
    try:
        analytics_engine = AnalyticsEngine(db_service)
        logger.info("✅ Analytics engine initialized")
    except Exception as e:
        logger.warning(f"⚠️ Analytics engine not available: {e}")
        analytics_engine = None
    
    logger.info("🎯 Ready for Priority 4 - Data Visualization Development!")

# Pydantic models for request/response
from pydantic import BaseModel
from decimal import Decimal

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category: Optional[str] = None
    date: Optional[date] = None

class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: float
    category: str
    date: date
    ai_confidence: Optional[float] = None
    ai_method: Optional[str] = None
    created_at: datetime

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "app": "AI Budget Tracker v3.0",
        "status": "operational",
        "version": "3.0.0",
        "features": {
            "ai_categorization": True,
            "database_persistence": db_service is not None,
            "analytics_engine": analytics_engine is not None,
            "data_visualization": "Priority 4 - In Development"
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "expenses": "/expenses",
            "analytics": "/analytics",
            "visualizations": "/visualizations"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_categorizer": True,
            "database": db_service is not None,
            "analytics": analytics_engine is not None
        }
    }

# AI Categorization endpoint
@app.post("/categorize")
async def categorize_expense(expense_data: ExpenseCreate):
    """Categorize an expense using AI"""
    try:
        result = await ai_categorizer.categorize_expense(
            expense_data.description, 
            expense_data.amount
        )
        
        return {
            "description": expense_data.description,
            "amount": expense_data.amount,
            "suggested_category": result["category"],
            "confidence": result["confidence"],
            "method": result["method"],
            "success": result["success"]
        }
    
    except Exception as e:
        logger.error(f"Categorization error: {e}")
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")

# Expenses endpoints
@app.post("/expenses", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate):
    """Create a new expense with AI categorization"""
    try:
        # AI categorization
        if not expense.category:
            ai_result = await ai_categorizer.categorize_expense(
                expense.description, 
                expense.amount
            )
            expense.category = ai_result["category"]
            ai_confidence = ai_result["confidence"]
            ai_method = ai_result["method"]
        else:
            ai_confidence = None
            ai_method = "manual"
        
        # Database storage (if available)
        if db_service:
            expense_id = await db_service.create_expense(
                description=expense.description,
                amount=expense.amount,
                category=expense.category,
                date=expense.date or date.today(),
                ai_confidence=ai_confidence,
                ai_method=ai_method
            )
            
            return ExpenseResponse(
                id=expense_id,
                description=expense.description,
                amount=expense.amount,
                category=expense.category,
                date=expense.date or date.today(),
                ai_confidence=ai_confidence,
                ai_method=ai_method,
                created_at=datetime.now()
            )
        else:
            # Mock response when database not available
            return ExpenseResponse(
                id=999,
                description=expense.description,
                amount=expense.amount,
                category=expense.category,
                date=expense.date or date.today(),
                ai_confidence=ai_confidence,
                ai_method=ai_method,
                created_at=datetime.now()
            )
    
    except Exception as e:
        logger.error(f"Expense creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create expense: {str(e)}")

@app.get("/expenses")
async def get_expenses(limit: int = 100):
    """Get all expenses"""
    if db_service:
        try:
            expenses = await db_service.get_expenses(limit=limit)
            return {"expenses": expenses, "count": len(expenses)}
        except Exception as e:
            logger.error(f"Database error: {e}")
            return {"expenses": [], "count": 0, "error": "Database not available"}
    else:
        # Mock data for development
        return {
            "expenses": [
                {
                    "id": 1,
                    "description": "Grocery shopping at Walmart",
                    "amount": 67.89,
                    "category": "Food and Dining",
                    "date": "2025-01-25",
                    "ai_confidence": 0.95,
                    "ai_method": "local_ai"
                },
                {
                    "id": 2,
                    "description": "Gas station fill-up",
                    "amount": 45.50,
                    "category": "Transportation",
                    "date": "2025-01-24",
                    "ai_confidence": 0.88,
                    "ai_method": "local_ai"
                },
                {
                    "id": 3,
                    "description": "Netflix subscription",
                    "amount": 15.99,
                    "category": "Entertainment",
                    "date": "2025-01-23",
                    "ai_confidence": 0.92,
                    "ai_method": "local_ai"
                }
            ],
            "count": 3,
            "note": "Mock data - database not connected"
        }

# Analytics endpoints
@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get spending analytics summary"""
    if analytics_engine:
        try:
            summary = await analytics_engine.generate_summary_analytics()
            return summary
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            # Return mock data on error
            pass
    
    # Mock analytics data for development
    return {
        "total_spending": 153.38,
        "expense_count": 5,
        "average_confidence": 0.92,
        "top_categories": [
            {"category": "Food and Dining", "amount": 67.89, "percentage": 44.3},
            {"category": "Transportation", "amount": 45.50, "percentage": 29.7},
            {"category": "Entertainment", "amount": 39.99, "percentage": 26.0}
        ],
        "insights": [
            {
                "type": "high_spending",
                "category": "Food and Dining",
                "message": "Food and Dining accounts for 44.3% of your spending ($67.89). Consider meal planning and bulk purchasing to optimize costs.",
                "confidence": 0.90,
                "priority": "medium"
            }
        ],
        "recommendations": [
            {
                "title": "Optimize Food Spending",
                "description": "Based on your patterns, meal planning could save you approximately $15.75 per month.",
                "actions": ["Plan meals weekly", "Cook at home more often", "Use grocery lists"],
                "potential_savings": 15.75
            }
        ],
        "ai_performance": {
            "total_categorizations": 5,
            "average_confidence": 0.92,
            "method_breakdown": {
                "local_ai": 4,
                "keyword": 1,
                "manual": 0
            }
        },
        "note": "Mock data - full analytics engine not connected"
    }

# Data Visualization endpoints (Priority 4)
@app.get("/visualizations/charts")
async def get_chart_data():
    """Get data for charts and visualizations"""
    return {
        "category_breakdown": {
            "labels": ["Food and Dining", "Transportation", "Entertainment"],
            "values": [67.89, 45.50, 39.99],
            "colors": ["#FF6384", "#36A2EB", "#FFCE56"]
        },
        "spending_trends": {
            "dates": ["2025-01-21", "2025-01-22", "2025-01-23", "2025-01-24", "2025-01-25"],
            "amounts": [0, 12.50, 15.99, 45.50, 67.89]
        },
        "ai_confidence_over_time": {
            "dates": ["2025-01-21", "2025-01-22", "2025-01-23", "2025-01-24", "2025-01-25"],
            "confidence": [0, 0.85, 0.92, 0.88, 0.95]
        },
        "budget_vs_actual": {
            "categories": ["Food and Dining", "Transportation", "Entertainment"],
            "budgeted": [100, 80, 50],
            "actual": [67.89, 45.50, 39.99]
        }
    }

# Model information endpoint
@app.get("/ai/info")
async def get_ai_info():
    """Get AI model information"""
    try:
        info = ai_categorizer.get_model_info()
        return info
    except Exception as e:
        return {"error": f"Failed to get AI info: {str(e)}"}

# Categories endpoint
@app.get("/categories")
async def get_categories():
    """Get available expense categories"""
    try:
        categories = ai_categorizer.get_categories()
        return {"categories": categories}
    except Exception as e:
        return {"categories": [], "error": str(e)}

# Static files for frontend (if needed)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    logger.info("No static directory found - skipping static file mounting")

# Serve the demo analytics page
@app.get("/demo")
async def serve_demo():
    """Serve the demo analytics page"""
    try:
        return FileResponse("demo_analytics.html")
    except FileNotFoundError:
        return {"message": "Demo page not found", "docs": "/docs"}

# Serve Priority 4 dashboard
@app.get("/priority4")
async def serve_priority4_dashboard():
    """Serve the Priority 4 interactive dashboard"""
    try:
        return FileResponse("priority4_dashboard.html")
    except FileNotFoundError:
        return {"message": "Priority 4 dashboard not found", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
