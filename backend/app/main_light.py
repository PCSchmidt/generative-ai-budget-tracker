"""
Lightweight main.py for Railway deployment
Uses API-based AI instead of local models to reduce Docker image size
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from datetime import datetime, date
from typing import Optional, Dict, List

# Import lightweight services
try:
    # Try relative imports first (for uvicorn)
    from .ai_categorizer_light import lightweight_categorizer
    from .expense_db import expense_db
    from .spending_analyzer import spending_analyzer
    from .visualization_api import viz_router, viz_service
except ImportError:
    # Fall back to absolute imports (for direct execution)
    from ai_categorizer_light import lightweight_categorizer
    from expense_db import expense_db
    from spending_analyzer import spending_analyzer
    from visualization_api import viz_router, viz_service

# Create FastAPI application
app = FastAPI(
    title="AI Budget Tracker API - Lightweight",
    description="Smart expense tracking with API-based AI categorization (Railway optimized)",
    version="3.1.0-light"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(viz_router)

# Pydantic models for request/response
class ExpenseRequest(BaseModel):
    description: str
    amount: float
    category: Optional[str] = None
    expense_date: Optional[str] = None  # ISO date string
    notes: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: float
    category: str
    category_confidence: float
    categorization_method: str
    date_created: str
    expense_date: str

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await expense_db.init_pool()
    
    # Initialize visualization service with database connections
    viz_service.expense_db = expense_db
    viz_service.spending_analyzer = spending_analyzer

# In-memory storage for fallback (will be removed once database is stable)
expenses_storage: List[Dict] = []
expense_counter = 1

@app.get("/")
async def root():
    """Root endpoint with database status"""
    database_status = "connected" if expense_db.pool else "not_connected"
    
    return {
        "message": "🤖 AI Budget Tracker API - Lightweight Version!",
        "version": "3.1.0-light",
        "status": "healthy",
        "deployment": "railway",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "database_status": database_status,
        "ai_features": {
            "expense_categorization": True,
            "database_persistence": database_status == "connected",
            "huggingface_configured": bool(os.getenv("HUGGINGFACE_API_KEY")),
            "groq_configured": bool(os.getenv("GROQ_API_KEY")),
            "deployment_type": "lightweight"
        }
    }

@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy", "service": "ai-budget-tracker-light"}

@app.post("/api/ai/categorize")
async def categorize_expense_endpoint(request: ExpenseRequest):
    """AI-powered expense categorization endpoint (lightweight)"""
    try:
        # Use our lightweight AI categorizer
        categorization_result = await lightweight_categorizer.categorize_expense(
            description=request.description,
            amount=request.amount
        )
        
        return {
            "success": True,
            "description": request.description,
            "amount": request.amount,
            "suggested_category": categorization_result["category"],
            "confidence": categorization_result["confidence"],
            "method": categorization_result["method"],
            "alternatives": categorization_result.get("all_predictions", []),
            "timestamp": datetime.now().isoformat(),
            "api_type": "lightweight"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")

@app.post("/api/expenses", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseRequest):
    """Create a new expense with AI categorization and database storage"""
    global expense_counter
    
    try:
        # AI categorization
        if not expense.category:
            categorization_result = await lightweight_categorizer.categorize_expense(
                description=expense.description,
                amount=expense.amount
            )
            
            category = categorization_result["category"]
            confidence = categorization_result["confidence"]
            method = categorization_result["method"]
        else:
            category = expense.category
            confidence = 1.0
            method = "manual"
        
        # Parse expense date
        if expense.expense_date:
            try:
                expense_date = datetime.fromisoformat(expense.expense_date.replace('Z', '+00:00')).date()
            except:
                expense_date = date.today()
        else:
            expense_date = date.today()
        
        # Try database insertion
        try:
            if expense_db.pool:
                expense_id = await expense_db.create_expense(
                    description=expense.description,
                    amount=expense.amount,
                    category=category,
                    category_confidence=confidence,
                    categorization_method=method,
                    expense_date=expense_date,
                    notes=expense.notes
                )
                
                # Retrieve the created expense
                created_expense = await expense_db.get_expense(expense_id)
                
                return ExpenseResponse(
                    id=created_expense["id"],
                    description=created_expense["description"],
                    amount=created_expense["amount"],
                    category=created_expense["category"],
                    category_confidence=created_expense["category_confidence"],
                    categorization_method=created_expense["categorization_method"],
                    date_created=created_expense["date_created"].isoformat(),
                    expense_date=created_expense["expense_date"].isoformat()
                )
                
        except Exception as db_error:
            print(f"Database error: {db_error}")
            # Fall back to in-memory storage
            pass
        
        # Fallback to in-memory storage
        expense_data = {
            "id": expense_counter,
            "description": expense.description,
            "amount": expense.amount,
            "category": category,
            "category_confidence": confidence,
            "categorization_method": method,
            "date_created": datetime.now(),
            "expense_date": expense_date,
            "notes": expense.notes
        }
        
        expenses_storage.append(expense_data)
        expense_counter += 1
        
        return ExpenseResponse(
            id=expense_data["id"],
            description=expense_data["description"],
            amount=expense_data["amount"],
            category=expense_data["category"],
            category_confidence=expense_data["category_confidence"],
            categorization_method=expense_data["categorization_method"],
            date_created=expense_data["date_created"].isoformat(),
            expense_date=expense_data["expense_date"].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create expense: {str(e)}")

@app.get("/api/expenses")
async def get_expenses(limit: int = 10, offset: int = 0):
    """Get expenses with pagination"""
    try:
        if expense_db.pool:
            expenses = await expense_db.get_expenses(limit=limit, offset=offset)
            
            return {
                "status": "success",
                "expenses": [
                    {
                        "id": exp["id"],
                        "description": exp["description"],
                        "amount": exp["amount"],
                        "category": exp["category"],
                        "category_confidence": exp["category_confidence"],
                        "categorization_method": exp["categorization_method"],
                        "date_created": exp["date_created"].isoformat(),
                        "expense_date": exp["expense_date"].isoformat(),
                        "notes": exp.get("notes")
                    }
                    for exp in expenses
                ],
                "total": len(expenses),
                "limit": limit,
                "offset": offset,
                "source": "database"
            }
    except Exception as e:
        print(f"Database query error: {e}")
    
    # Fallback to in-memory data
    start_idx = offset
    end_idx = offset + limit
    expenses_slice = expenses_storage[start_idx:end_idx]
    
    return {
        "status": "success", 
        "expenses": [
            {
                "id": exp["id"],
                "description": exp["description"],
                "amount": exp["amount"],
                "category": exp["category"],
                "category_confidence": exp["category_confidence"],
                "categorization_method": exp["categorization_method"],
                "date_created": exp["date_created"].isoformat(),
                "expense_date": exp["expense_date"].isoformat(),
                "notes": exp.get("notes")
            }
            for exp in expenses_slice
        ],
        "total": len(expenses_storage),
        "limit": limit,
        "offset": offset,
        "source": "memory_fallback"
    }

@app.get("/api/analytics/patterns")
async def get_spending_patterns(days: int = 30):
    """Get spending pattern analysis"""
    try:
        if spending_analyzer and expense_db.pool:
            analysis = await spending_analyzer.analyze_spending_patterns(days=days)
            return {
                "status": "success",
                "analysis": analysis,
                "period_days": days,
                "timestamp": datetime.now().isoformat(),
                "source": "database_analytics"
            }
    except Exception as e:
        print(f"Analytics error: {e}")
    
    # Fallback analytics using in-memory data
    return {
        "status": "success",
        "analysis": {
            "total_amount": sum(exp["amount"] for exp in expenses_storage),
            "total_expenses": len(expenses_storage),
            "patterns": {
                "categories": _analyze_categories(expenses_storage)
            },
            "ai_stats": _analyze_ai_performance(expenses_storage)
        },
        "period_days": days,
        "timestamp": datetime.now().isoformat(),
        "source": "memory_analytics"
    }

def _analyze_categories(expenses: List[Dict]) -> Dict:
    """Analyze category breakdown"""
    categories = {}
    for expense in expenses:
        category = expense.get("category", "Other")
        if category not in categories:
            categories[category] = {"amount": 0, "count": 0}
        categories[category]["amount"] += expense.get("amount", 0)
        categories[category]["count"] += 1
    return categories

def _analyze_ai_performance(expenses: List[Dict]) -> Dict:
    """Analyze AI performance metrics"""
    methods = {}
    total_confidence = 0
    
    for expense in expenses:
        method = expense.get("categorization_method", "unknown")
        confidence = expense.get("category_confidence", 0)
        
        if method not in methods:
            methods[method] = 0
        methods[method] += 1
        total_confidence += confidence
    
    avg_confidence = total_confidence / len(expenses) if expenses else 0
    
    return {
        "methods": methods,
        "average_confidence": avg_confidence,
        "ai_categorized": methods.get("huggingface_api", 0) + methods.get("groq_api", 0),
        "keyword_categorized": methods.get("keyword_match", 0),
        "manual_categorized": methods.get("manual", 0)
    }

@app.get("/api/analytics/insights")
async def get_insights(days: int = 30):
    """Get AI-generated insights"""
    try:
        if spending_analyzer and expense_db.pool:
            insights = await spending_analyzer.generate_insights(days=days)
            recommendations = await spending_analyzer.generate_recommendations(days=days)
            
            return {
                "status": "success",
                "insights": insights,
                "recommendations": recommendations,
                "period_days": days,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Insights error: {e}")
    
    # Fallback insights
    return {
        "status": "success",
        "insights": [
            "Your spending is being tracked and categorized with AI",
            f"You have {len(expenses_storage)} expenses totaling ${sum(exp['amount'] for exp in expenses_storage):.2f}"
        ],
        "recommendations": [
            "Continue tracking expenses to build better insights",
            "Add more detailed descriptions for better AI categorization"
        ],
        "period_days": days,
        "timestamp": datetime.now().isoformat(),
        "source": "fallback_insights"
    }

@app.get("/priority4", response_class=HTMLResponse)
async def get_priority4_dashboard():
    """Serve the Priority 4 interactive dashboard"""
    try:
        dashboard_path = os.path.join(os.path.dirname(__file__), "priority4_dashboard.html")
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        else:
            return HTMLResponse(content="""
            <html><body>
                <h1>Priority 4 Dashboard</h1>
                <p>Dashboard file not found. API endpoints are available at:</p>
                <ul>
                    <li><a href="/docs">API Documentation</a></li>
                    <li><a href="/expenses">Expenses API</a></li>
                    <li><a href="/analytics/summary">Analytics Summary</a></li>
                </ul>
            </body></html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error loading dashboard: {str(e)}</h1></body></html>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
