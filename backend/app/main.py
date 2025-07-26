"""
AI Budget Tracker - Enhanced FastAPI with AI Categorization
Now includes real AI-powered expense categorization
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime
from typing import Optional, Dict, List

# Import our AI categorization service
from ai_categorizer import expense_categorizer

# Create FastAPI application
app = FastAPI(
    title="AI Budget Tracker API",
    description="Smart expense tracking with AI-powered categorization",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ExpenseRequest(BaseModel):
    description: str
    amount: float
    category: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: float
    category: str
    category_confidence: float
    categorization_method: str
    date_created: str

# In-memory storage for demo (will be replaced with database)
expenses_storage: List[Dict] = []
expense_counter = 1

@app.get("/")
async def root():
    """Root endpoint - Railway health check"""
    return {
        "message": "🤖 AI Budget Tracker API with AI Categorization!",
        "version": "2.0.0-ai-enabled",
        "status": "healthy",
        "deployment": "railway",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "ai_features": {
            "expense_categorization": True,
            "huggingface_configured": bool(os.getenv("HUGGINGFACE_API_KEY")),
            "groq_configured": bool(os.getenv("GROQ_API_KEY"))
        }
    }

@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy", "service": "ai-budget-tracker-enhanced"}

@app.post("/api/ai/categorize")
async def categorize_expense_endpoint(request: ExpenseRequest):
    """AI-powered expense categorization endpoint"""
    try:
        # Use our AI categorizer
        categorization_result = await expense_categorizer.categorize_expense(
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
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")

@app.post("/api/expenses")
async def create_expense(request: ExpenseRequest):
    """Create a new expense with AI categorization"""
    global expense_counter
    
    try:
        # If no category provided, use AI to categorize
        if not request.category:
            categorization_result = await expense_categorizer.categorize_expense(
                description=request.description,
                amount=request.amount
            )
            category = categorization_result["category"]
            category_confidence = categorization_result["confidence"]
            categorization_method = categorization_result["method"]
        else:
            category = request.category
            category_confidence = 1.0
            categorization_method = "manual"
        
        # Create expense record
        expense = {
            "id": expense_counter,
            "description": request.description,
            "amount": request.amount,
            "category": category,
            "category_confidence": category_confidence,
            "categorization_method": categorization_method,
            "date_created": datetime.now().isoformat()
        }
        
        expenses_storage.append(expense)
        expense_counter += 1
        
        return {
            "success": True,
            "expense": expense,
            "message": f"Expense created and categorized as {category}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create expense: {str(e)}")

@app.get("/api/expenses")
async def get_expenses():
    """Get all expenses with AI categorization data"""
    return {
        "expenses": expenses_storage,
        "total": len(expenses_storage),
        "total_amount": sum(expense["amount"] for expense in expenses_storage),
        "ai_categorized": len([e for e in expenses_storage if e["categorization_method"] in ["ai_classification", "keyword_matching"]]),
        "manual_categorized": len([e for e in expenses_storage if e["categorization_method"] == "manual"]),
        "categories": list(set(expense["category"] for expense in expenses_storage)) if expenses_storage else []
    }

@app.get("/api/insights")
async def get_insights():
    """Generate AI-powered financial insights from expenses"""
    if not expenses_storage:
        return {
            "insights": {
                "advice": "No expenses tracked yet. Start adding expenses to get personalized AI insights!",
                "total_tracked": 0,
                "categories": []
            },
            "ai_status": "ready"
        }
    
    # Calculate spending by category
    category_totals = {}
    for expense in expenses_storage:
        category = expense["category"]
        category_totals[category] = category_totals.get(category, 0) + expense["amount"]
    
    # Find top spending category
    top_category = max(category_totals, key=category_totals.get) if category_totals else "Unknown"
    top_amount = category_totals.get(top_category, 0)
    total_spending = sum(category_totals.values())
    
    # Generate AI advice
    advice = f"Your biggest spending category is {top_category} (${top_amount:.2f}). "
    if top_amount > total_spending * 0.4:
        advice += "This represents a large portion of your budget - consider setting spending limits!"
    else:
        advice += "Your spending seems well distributed across categories."
    
    return {
        "insights": {
            "advice": advice,
            "top_category": top_category,
            "top_amount": top_amount,
            "total_tracked": total_spending,
            "category_breakdown": category_totals,
            "expense_count": len(expenses_storage)
        },
        "ai_status": "enhanced"
    }

# Start the application (Railway deployment pattern)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
