"""
AI Budget Tracker - Enhanced FastAPI with Database Persistence
Now includes real AI-powered expense categorization and PostgreSQL storage
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime, date
from typing import Optional, Dict, List

# Import our services
try:
    # Try relative imports first (for uvicorn)
    from .ai_categorizer import expense_categorizer
    from .expense_db import expense_db
    from .spending_analyzer import spending_analyzer
    from .visualization_api import viz_router, viz_service
except ImportError:
    # Fall back to absolute imports (for direct execution)
    from ai_categorizer import expense_categorizer
    from expense_db import expense_db
    from spending_analyzer import spending_analyzer
    from visualization_api import viz_router, viz_service

# Create FastAPI application
app = FastAPI(
    title="AI Budget Tracker API",
    description="Smart expense tracking with AI-powered categorization and database persistence",
    version="2.1.0"
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
        "message": "🤖 AI Budget Tracker API with Database Persistence!",
        "version": "2.1.0-database-enabled",
        "status": "healthy",
        "deployment": "railway",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "database_status": database_status,
        "ai_features": {
            "expense_categorization": True,
            "database_persistence": database_status == "connected",
            "huggingface_configured": bool(os.getenv("HUGGINGFACE_API_KEY")),
            "groq_configured": bool(os.getenv("GROQ_API_KEY"))
        }
    }

@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy", "service": "ai-budget-tracker-database"}

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
    """Create a new expense with AI categorization and database storage"""
    global expense_counter
    
    try:
        # If no category provided, use AI to categorize
        categorization_result = None
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
        
        # Parse expense date
        expense_date = date.today()
        if request.expense_date:
            try:
                expense_date = datetime.fromisoformat(request.expense_date.replace('Z', '+00:00')).date()
            except:
                expense_date = date.today()
        
        # Prepare expense data for database
        expense_data = {
            "description": request.description,
            "amount": request.amount,
            "category": category,
            "category_confidence": category_confidence,
            "categorization_method": categorization_method,
            "expense_date": expense_date,
            "user_id": "default_user",
            "notes": request.notes,
            "ai_data": categorization_result if categorization_result else {}
        }
        
        # Try to save to database first
        try:
            if expense_db.pool:
                db_expense = await expense_db.create_expense(expense_data)
                
                return {
                    "success": True,
                    "expense": {
                        "id": db_expense["id"],
                        "description": db_expense["description"],
                        "amount": float(db_expense["amount"]),
                        "category": db_expense["category"],
                        "category_confidence": float(db_expense["category_confidence"]),
                        "categorization_method": db_expense["categorization_method"],
                        "date_created": db_expense["date_created"],
                        "expense_date": db_expense["expense_date"]
                    },
                    "storage": "database",
                    "message": f"Expense saved to database and categorized as {category}",
                    "ai_confidence": category_confidence if categorization_result else None
                }
            else:
                raise Exception("Database not available")
                
        except Exception as db_error:
            # Fallback to in-memory storage
            expense = {
                "id": expense_counter,
                "description": request.description,
                "amount": request.amount,
                "category": category,
                "category_confidence": category_confidence,
                "categorization_method": categorization_method,
                "date_created": datetime.now().isoformat(),
                "expense_date": expense_date.isoformat(),
                "notes": request.notes
            }
            
            expenses_storage.append(expense)
            expense_counter += 1
            
            return {
                "success": True,
                "expense": expense,
                "storage": "memory_fallback",
                "message": f"Expense saved (fallback mode) and categorized as {category}",
                "ai_confidence": category_confidence if categorization_result else None,
                "warning": f"Database unavailable: {str(db_error)}"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create expense: {str(e)}")

@app.get("/api/expenses")
async def get_expenses(limit: int = 50):
    """Get all expenses from database with AI categorization data"""
    try:
        # Try to get from database first
        if expense_db.pool:
            try:
                db_expenses = await expense_db.get_expenses(limit=limit)
                
                # Calculate statistics
                total_amount = sum(float(exp["amount"]) for exp in db_expenses)
                ai_categorized = len([e for e in db_expenses if e["categorization_method"] in ["ai_classification", "keyword_matching"]])
                manual_categorized = len([e for e in db_expenses if e["categorization_method"] == "manual"])
                categories = list(set(exp["category"] for exp in db_expenses)) if db_expenses else []
                
                return {
                    "expenses": db_expenses,
                    "total": len(db_expenses),
                    "total_amount": total_amount,
                    "ai_categorized": ai_categorized,
                    "manual_categorized": manual_categorized,
                    "categories": categories,
                    "storage": "database"
                }
                
            except Exception as db_error:
                # Fallback to in-memory storage
                return {
                    "expenses": expenses_storage,
                    "total": len(expenses_storage),
                    "total_amount": sum(expense["amount"] for expense in expenses_storage),
                    "ai_categorized": len([e for e in expenses_storage if e.get("categorization_method") in ["ai_classification", "keyword_matching"]]),
                    "manual_categorized": len([e for e in expenses_storage if e.get("categorization_method") == "manual"]),
                    "categories": list(set(expense["category"] for expense in expenses_storage)) if expenses_storage else [],
                    "storage": "memory_fallback",
                    "warning": f"Database error: {str(db_error)}"
                }
        else:
            # Database not available, use memory storage
            return {
                "expenses": expenses_storage,
                "total": len(expenses_storage),
                "total_amount": sum(expense["amount"] for expense in expenses_storage),
                "ai_categorized": len([e for e in expenses_storage if e.get("categorization_method") in ["ai_classification", "keyword_matching"]]),
                "manual_categorized": len([e for e in expenses_storage if e.get("categorization_method") == "manual"]),
                "categories": list(set(expense["category"] for expense in expenses_storage)) if expenses_storage else [],
                "storage": "memory_only"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get expenses: {str(e)}")

@app.get("/api/insights")
async def get_insights(days: int = 30):
    """Generate AI-powered financial insights from database or memory"""
    try:
        # Try to get analytics from database
        if expense_db.pool:
            try:
                analytics = await expense_db.get_spending_analytics(days=days)
                
                if analytics['total_expenses'] == 0:
                    return {
                        "insights": {
                            "advice": "No expenses tracked yet. Start adding expenses to get personalized AI insights!",
                            "total_tracked": 0,
                            "categories": [],
                            "period_days": days
                        },
                        "ai_status": "ready",
                        "storage": "database"
                    }
                
                # Generate AI advice based on database analytics
                top_category = analytics['categories'][0] if analytics['categories'] else None
                total_spending = analytics['total_amount']
                
                if top_category:
                    advice = f"Your biggest spending category is {top_category['category']} (${top_category['amount']:.2f}). "
                    if top_category['amount'] > total_spending * 0.4:
                        advice += "This represents a large portion of your budget - consider setting spending limits!"
                    else:
                        advice += "Your spending seems well distributed across categories."
                    
                    # Add AI-specific insights
                    ai_stats = analytics['ai_stats']
                    if ai_stats['ai_categorized'] > 0:
                        advice += f" AI has helped categorize {ai_stats['ai_categorized']} expenses with {ai_stats['average_confidence']*100:.0f}% average confidence."
                else:
                    advice = f"You've spent ${total_spending:.2f} over {days} days. Keep tracking to build better financial habits!"
                
                return {
                    "insights": {
                        "advice": advice,
                        "top_category": top_category['category'] if top_category else "None",
                        "top_amount": top_category['amount'] if top_category else 0,
                        "total_tracked": total_spending,
                        "category_breakdown": {cat['category']: cat['amount'] for cat in analytics['categories']},
                        "expense_count": analytics['total_expenses'],
                        "ai_categorization_stats": analytics['ai_stats'],
                        "period_days": days
                    },
                    "ai_status": "enhanced_with_database",
                    "storage": "database"
                }
                
            except Exception as db_error:
                # Fallback to memory analytics
                return await get_memory_insights(days)
        else:
            # Database not available
            return await get_memory_insights(days)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

async def get_memory_insights(days: int = 30):
    """Fallback insights using in-memory storage"""
    if not expenses_storage:
        return {
            "insights": {
                "advice": "No expenses tracked yet. Start adding expenses to get personalized AI insights!",
                "total_tracked": 0,
                "categories": [],
                "period_days": days
            },
            "ai_status": "ready",
            "storage": "memory_fallback"
        }
    
    # Calculate spending by category from memory
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
            "expense_count": len(expenses_storage),
            "period_days": days
        },
        "ai_status": "memory_analysis",
        "storage": "memory"
    }

# Additional database endpoints

@app.get("/api/expenses/{expense_id}")
async def get_expense(expense_id: int):
    """Get a specific expense by ID"""
    try:
        if expense_db.pool:
            expense = await expense_db.get_expense_by_id(expense_id)
            if expense:
                return {"success": True, "expense": expense}
            else:
                raise HTTPException(status_code=404, detail="Expense not found")
        else:
            # Search in memory storage
            expense = next((e for e in expenses_storage if e["id"] == expense_id), None)
            if expense:
                return {"success": True, "expense": expense, "storage": "memory"}
            else:
                raise HTTPException(status_code=404, detail="Expense not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get expense: {str(e)}")

@app.delete("/api/expenses/{expense_id}")
async def delete_expense(expense_id: int):
    """Delete an expense by ID"""
    try:
        if expense_db.pool:
            success = await expense_db.delete_expense(expense_id)
            if success:
                return {"success": True, "message": "Expense deleted from database"}
            else:
                raise HTTPException(status_code=404, detail="Expense not found")
        else:
            # Delete from memory storage
            global expenses_storage
            original_count = len(expenses_storage)
            expenses_storage = [e for e in expenses_storage if e["id"] != expense_id]
            if len(expenses_storage) < original_count:
                return {"success": True, "message": "Expense deleted from memory", "storage": "memory"}
            else:
                raise HTTPException(status_code=404, detail="Expense not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete expense: {str(e)}")

@app.get("/api/analytics")
async def get_analytics(days: int = 30):
    """Get detailed spending analytics"""
    try:
        if expense_db.pool:
            analytics = await expense_db.get_spending_analytics(days=days)
            return {
                "success": True,
                "analytics": analytics,
                "storage": "database"
            }
        else:
            # Basic analytics from memory
            if not expenses_storage:
                return {
                    "success": True,
                    "analytics": {
                        "total_amount": 0,
                        "total_expenses": 0,
                        "categories": [],
                        "period_days": days
                    },
                    "storage": "memory"
                }
            
            category_totals = {}
            for expense in expenses_storage:
                category = expense["category"]
                category_totals[category] = category_totals.get(category, 0) + expense["amount"]
            
            return {
                "success": True,
                "analytics": {
                    "total_amount": sum(expense["amount"] for expense in expenses_storage),
                    "total_expenses": len(expenses_storage),
                    "categories": [
                        {"category": cat, "amount": amount, "count": 1}
                        for cat, amount in category_totals.items()
                    ],
                    "period_days": days
                },
                "storage": "memory"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# Priority 3: Advanced Spending Analytics Endpoints
@app.get("/api/analytics/patterns")
async def get_spending_patterns(days: int = 30):
    """Get comprehensive spending pattern analysis"""
    try:
        # Initialize spending analyzer with database connection
        spending_analyzer.expense_db = expense_db
        
        analysis = await spending_analyzer.analyze_spending_patterns(days=days)
        return {
            "status": "success",
            "analysis": analysis,
            "api_version": "3.0.0",
            "features": ["patterns", "insights", "recommendations", "anomalies"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

@app.get("/api/analytics/insights")
async def get_financial_insights(days: int = 30):
    """Get AI-generated financial insights"""
    try:
        spending_analyzer.expense_db = expense_db
        analysis = await spending_analyzer.analyze_spending_patterns(days=days)
        
        return {
            "status": "success",
            "insights": analysis["insights"],
            "recommendations": analysis["recommendations"],
            "period_days": days,
            "total_expenses": analysis["total_expenses"],
            "total_amount": analysis["total_amount"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@app.get("/api/analytics/anomalies")
async def detect_spending_anomalies(days: int = 30):
    """Detect unusual spending patterns"""
    try:
        spending_analyzer.expense_db = expense_db
        analysis = await spending_analyzer.analyze_spending_patterns(days=days)
        
        return {
            "status": "success",
            "anomalies": analysis["anomalies"],
            "anomaly_count": len(analysis["anomalies"]),
            "period_analyzed": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@app.get("/api/analytics/ai-performance")
async def get_ai_performance():
    """Get AI categorization performance metrics"""
    try:
        spending_analyzer.expense_db = expense_db
        analysis = await spending_analyzer.analyze_spending_patterns(days=90)  # 3 months
        
        ai_stats = analysis["ai_stats"]
        total = ai_stats["total_categorized"]
        
        performance = {
            "total_expenses": total,
            "ai_categorized": ai_stats["ai_categorized"],
            "keyword_categorized": ai_stats["keyword_categorized"], 
            "manual_categorized": ai_stats["manual_categorized"],
            "ai_percentage": (ai_stats["ai_categorized"] / total * 100) if total > 0 else 0,
            "average_confidence": ai_stats["average_confidence"],
            "high_confidence_count": ai_stats.get("high_confidence_count", 0),
            "efficiency_rating": "excellent" if ai_stats["average_confidence"] > 0.85 else 
                               "good" if ai_stats["average_confidence"] > 0.7 else "needs_improvement"
        }
        
        return {
            "status": "success",
            "performance": performance,
            "period_analyzed": 90
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI performance analysis failed: {str(e)}")

# Start the application (Railway deployment pattern)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
