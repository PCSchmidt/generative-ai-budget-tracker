"""
AI Budget Tracker FastAPI Backend
Phase 2: Core Integration Backend
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, date
from jose import jwt
import bcrypt
import os
import re
from pathlib import Path
import sys
import os

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # Go up one level to backend
sys.path.insert(0, current_dir)
sys.path.insert(0, backend_dir)

try:
    # Import from our new services directory
    from services.ml_categorizer import EnhancedExpenseCategorizer
    from services.financial_advisor import EnhancedFinancialAdvisor
    
    # Initialize global instances
    enhanced_categorizer = EnhancedExpenseCategorizer()
    financial_advisor = EnhancedFinancialAdvisor()
    
    # Define wrapper functions for compatibility
    async def categorize_expense_detailed(description: str, amount: float = None, user_id: str = None) -> dict:
        category = enhanced_categorizer.categorize(description, amount or 0, user_id)
        stats = enhanced_categorizer.get_classification_stats()
        
        return {
            "category": category,
            "confidence": 0.85,  # ML-based confidence
            "method": "enhanced_ml",
            "reasoning": f"Classified using enhanced ML categorization"
        }
    
    async def get_financial_advice(expenses: list, user_profile: dict = None, advice_type: str = "general") -> dict:
        # Convert expenses to spending data format
        spending_data = {
            "total_spending": sum(exp.get("amount", 0) for exp in expenses),
            "monthly_income": 5000.00,  # Mock income - would come from user profile
            "categories": {},
            "expense_count": len(expenses)
        }
        
        # Aggregate by category
        for exp in expenses:
            category = exp.get("category", "Other")
            amount = exp.get("amount", 0)
            spending_data["categories"][category] = spending_data["categories"].get(category, 0) + amount
        
        # Generate advice
        advice = financial_advisor.generate_advice(spending_data, use_ai=False)
        analysis = financial_advisor.analyze_spending_patterns(spending_data)
        
        return {
            "advice_type": advice_type,
            "main_advice": advice,
            "action_items": analysis.get("recommendations", []),
            "confidence": 0.8,
            "processing_method": "enhanced_ai",
            "insights": analysis.get("insights", [])
        }
    
    async def get_spending_insights(expenses: list) -> dict:
        # Convert to spending data format
        spending_data = {
            "total_spending": sum(exp.get("amount", 0) for exp in expenses),
            "categories": {},
            "expense_count": len(expenses)
        }
        
        for exp in expenses:
            category = exp.get("category", "Other")
            amount = exp.get("amount", 0)
            spending_data["categories"][category] = spending_data["categories"].get(category, 0) + amount
        
        analysis = financial_advisor.analyze_spending_patterns(spending_data)
        
        return {
            "spending_velocity": len(expenses),  # Simple metric
            "category_diversity": len(spending_data["categories"]),
            "total_spending": spending_data["total_spending"],
            "insights": analysis.get("insights", []),
            "recommendations": analysis.get("recommendations", []),
            "category_breakdown": spending_data["categories"]
        }
    
    AI_AVAILABLE = True
    ML_ENHANCED = True
    print("✅ Enhanced ML categorization and financial advisor loaded successfully")
    
except ImportError as e:
    print(f"⚠️  Enhanced ML services not available: {e}")
    ML_ENHANCED = False
    
    try:
        # Try basic AI categorization if available in app directory
        from ai_categorizer import categorize_expense_ai, categorize_expense_rules
        AI_AVAILABLE = True
        print("✅ Basic AI categorization loaded successfully")
    except ImportError as e2:
        print(f"⚠️  AI categorization not available: {e2}")
        AI_AVAILABLE = False
        
        # Define basic rule-based fallback
        def categorize_expense_rules(description: str) -> str:
            """Basic rule-based categorization"""
            description = description.lower()
            
            if any(word in description for word in ['coffee', 'starbucks', 'restaurant', 'food', 'dining']):
                return "Food & Dining"
            elif any(word in description for word in ['uber', 'lyft', 'gas', 'fuel', 'transportation']):
                return "Transportation"
            elif any(word in description for word in ['netflix', 'spotify', 'entertainment', 'movie']):
                return "Entertainment"
            elif any(word in description for word in ['amazon', 'shopping', 'store']):
                return "Shopping"
            elif any(word in description for word in ['gym', 'fitness', 'health']):
                return "Health & Fitness"
            else:
                return "Miscellaneous"
        
        async def categorize_expense_ai(description: str, amount: float = None) -> str:
            """Async wrapper for rule-based categorization"""
            return categorize_expense_rules(description)
    
    # Fallback functions if ML not available
    async def categorize_expense_detailed(description: str, amount: float = None, user_id: str = None) -> dict:
        return {
            "category": "Other",
            "confidence": 0.1,
            "method": "fallback",
            "reasoning": "ML services unavailable"
        }
    
    async def get_financial_advice(expenses: list, user_profile: dict = None, advice_type: str = "general") -> dict:
        return {
            "advice_type": advice_type,
            "main_advice": "Keep tracking your expenses to understand spending patterns.",
            "action_items": ["Continue tracking expenses", "Set up a basic budget"],
            "confidence": 0.3,
            "processing_method": "fallback"
        }
    
    async def get_spending_insights(expenses: list) -> dict:
        return {
            "spending_velocity": 0,
            "category_diversity": 0,
            "recommendations": []
        }

# Create FastAPI app
app = FastAPI(
    title="AI Budget Tracker API",
    description="Backend API for AI-powered expense tracking",
    version="2.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# In-memory storage (replace with database in production)
users_db = {}
expenses_db = {}
user_counter = 1
expense_counter = 1

# Utility functions (defined early for use in test data)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: int) -> str:
    payload = {"user_id": user_id, "exp": datetime.utcnow().timestamp() + 3600}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Initialize test data for development
def initialize_test_data():
    global user_counter, expense_counter
    
    # Add test user: demo@budgettracker.com / password123
    test_user = {
        "id": user_counter,
        "email": "demo@budgettracker.com",
        "password": hash_password("password123"),
        "first_name": "Demo",
        "last_name": "User",
        "created_at": datetime.utcnow()
    }
    users_db["demo@budgettracker.com"] = test_user
    user_counter += 1
    
    # Add some sample expenses for the demo user
    sample_expenses = [
        {
            "id": expense_counter,
            "user_id": test_user["id"],
            "description": "Coffee at Starbucks",
            "amount": 4.95,
            "category": "Food & Dining",
            "expense_date": date.today(),
            "notes": "Morning coffee",
            "created_at": datetime.utcnow()
        },
        {
            "id": expense_counter + 1,
            "user_id": test_user["id"],
            "description": "Uber ride home",
            "amount": 12.50,
            "category": "Transportation",
            "expense_date": date.today(),
            "notes": "",
            "created_at": datetime.utcnow()
        },
        {
            "id": expense_counter + 2,
            "user_id": test_user["id"],
            "description": "Netflix subscription",
            "amount": 15.99,
            "category": "Entertainment",
            "expense_date": date.today(),
            "notes": "Monthly subscription",
            "created_at": datetime.utcnow()
        }
    ]
    
    for expense in sample_expenses:
        expenses_db[expense["id"]] = expense
        expense_counter += 1
    
    print(f"✅ Test data initialized: 1 user, {len(sample_expenses)} expenses")

# Initialize test data when the module loads
initialize_test_data()

# Pydantic models
class UserSignup(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    
    @validator('email')
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

class UserLogin(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category: Optional[str] = None
    expense_date: Optional[date] = None
    notes: Optional[str] = ""

class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    expense_date: Optional[date] = None
    notes: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: float
    category: str
    expense_date: date
    notes: str
    created_at: datetime

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str

class TokenResponse(BaseModel):
    access_token: str
    user: UserResponse

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Find user by ID from all users in the database
        user = None
        for email, user_data in users_db.items():
            if user_data["id"] == user_id:
                user = user_data
                break
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def categorize_expense(description: str, amount: float = None) -> str:
    """AI-powered expense categorization with rule-based fallback"""
    try:
        # Try AI categorization first
        category = await categorize_expense_ai(description, amount)
        return category
    except Exception as e:
        print(f"⚠️ AI categorization failed, using rules: {e}")
        # Fallback to rule-based categorization
        return categorize_expense_rules(description)

def categorize_expense_sync(description: str) -> str:
    """Synchronous version for backward compatibility"""
    return categorize_expense_rules(description)

# Routes
@app.get("/")
async def root():
    return {"message": "AI Budget Tracker API", "version": "2.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# Test AI categorization endpoint with better error handling
@app.post("/api/categorize-test")
async def test_categorization(description: str, amount: float = None):
    """Test endpoint for AI expense categorization"""
    print(f"🔍 Debug: Received request - description='{description}', amount={amount}")
    print(f"🔍 Debug: AI_AVAILABLE={AI_AVAILABLE}, ML_ENHANCED={ML_ENHANCED}")
    
    try:
        # Check if functions exist
        print(f"🔍 Debug: Checking function availability...")
        
        if ML_ENHANCED:
            print(f"🔍 Debug: Using ML Enhanced categorization")
            result = await categorize_expense_detailed(description, amount)
            category = result["category"]
            method = f"ML Enhanced: {result['method']}"
        else:
            print(f"🔍 Debug: Using basic categorization")
            category = await categorize_expense(description, amount)
            method = "Basic AI with rule-based fallback"
        
        print(f"✅ Debug: Successfully categorized '{description}' as '{category}'")
        
        return {
            "description": description,
            "amount": amount,
            "predicted_category": category,
            "method": method,
            "timestamp": datetime.utcnow(),
            "debug_info": {
                "ai_available": AI_AVAILABLE,
                "ml_enhanced": ML_ENHANCED
            }
        }
    except Exception as e:
        print(f"❌ Debug: Error in categorization: {str(e)}")
        import traceback
        print(f"❌ Debug: Full traceback: {traceback.format_exc()}")
        
        # Try fallback
        try:
            fallback_category = categorize_expense_rules(description)
            print(f"✅ Debug: Fallback successful: '{fallback_category}'")
            
            return {
                "description": description,
                "amount": amount,
                "predicted_category": fallback_category,
                "method": "Rule-based fallback (after error)",
                "error": str(e),
                "debug_info": {
                    "ai_available": AI_AVAILABLE,
                    "ml_enhanced": ML_ENHANCED,
                    "error_occurred": True
                }
            }
        except Exception as fallback_error:
            print(f"❌ Debug: Even fallback failed: {str(fallback_error)}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": "Categorization completely failed",
                    "original_error": str(e),
                    "fallback_error": str(fallback_error),
                    "debug_info": {
                        "ai_available": AI_AVAILABLE,
                        "ml_enhanced": ML_ENHANCED
                    }
                }
            )

# Authentication routes
@app.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    global user_counter
    
    # Check if user exists
    for user in users_db.values():
        if user["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = user_counter
    user_counter += 1
    
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    users_db[user_id] = user
    
    # Create token
    token = create_access_token(user_id)
    
    # Return user without password
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"]
    )
    
    return TokenResponse(access_token=token, user=user_response)

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    # Find user
    user = None
    for u in users_db.values():
        if u["email"] == user_data.email:
            user = u
            break
    
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create token
    token = create_access_token(user["id"])
    
    # Return user without password
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"]
    )
    
    return TokenResponse(access_token=token, user=user_response)

# Expense routes
@app.get("/api/expenses", response_model=List[ExpenseResponse])
async def get_expenses(current_user=Depends(get_current_user)):
    user_expenses = []
    for expense in expenses_db.values():
        if expense["user_id"] == current_user["id"]:
            user_expenses.append(ExpenseResponse(**expense))
    
    # Sort by date (newest first)
    user_expenses.sort(key=lambda x: x.created_at, reverse=True)
    return user_expenses

@app.post("/api/expenses", response_model=ExpenseResponse)
async def create_expense(expense_data: ExpenseCreate, current_user=Depends(get_current_user)):
    global expense_counter
    
    # Enhanced auto-categorization with ML
    if expense_data.category:
        category = expense_data.category
        categorization_info = {
            "category": category,
            "confidence": 1.0,
            "method": "user_provided",
            "reasoning": "Category provided by user"
        }
    else:
        try:
            if ML_ENHANCED:
                # Use enhanced ML categorization
                categorization_result = await categorize_expense_detailed(
                    description=expense_data.description,
                    amount=expense_data.amount,
                    user_id=str(current_user["id"])
                )
                category = categorization_result["category"]
                categorization_info = categorization_result
                print(f"✅ Enhanced ML categorized '{expense_data.description}' as '{category}' ({categorization_result['confidence']:.2f} confidence)")
            else:
                # Fallback to basic categorization
                if AI_AVAILABLE:
                    category = await categorize_expense_ai(expense_data.description, expense_data.amount)
                else:
                    category = categorize_expense_rules(expense_data.description)
                
                categorization_info = {
                    "category": category,
                    "confidence": 0.5,
                    "method": "basic_ai" if AI_AVAILABLE else "rules",
                    "reasoning": "Basic categorization"
                }
                print(f"✅ Basic categorized '{expense_data.description}' as '{category}'")
        
        except Exception as e:
            print(f"❌ Categorization failed: {e}")
            category = "Other"
            categorization_info = {
                "category": "Other",
                "confidence": 0.1,
                "method": "error_fallback",
                "reasoning": f"Categorization error: {str(e)}"
            }
    
    expense_id = expense_counter
    expense_counter += 1
    
    expense = {
        "id": expense_id,
        "user_id": current_user["id"],
        "description": expense_data.description,
        "amount": expense_data.amount,
        "category": category,
        "expense_date": expense_data.expense_date or date.today(),
        "notes": expense_data.notes,
        "created_at": datetime.utcnow(),
        # Store categorization metadata for debugging/learning
        "categorization_meta": categorization_info
    }
    
    expenses_db[expense_id] = expense
    
    # Create response without categorization metadata (keep API clean)
    response_data = {k: v for k, v in expense.items() if k != "categorization_meta"}
    
    return ExpenseResponse(**response_data)

@app.get("/api/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int, current_user=Depends(get_current_user)):
    expense = expenses_db.get(expense_id)
    
    if not expense or expense["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return ExpenseResponse(**expense)

@app.put("/api/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: int, expense_data: ExpenseUpdate, current_user=Depends(get_current_user)):
    expense = expenses_db.get(expense_id)
    
    if not expense or expense["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update fields
    if expense_data.description is not None:
        expense["description"] = expense_data.description
    if expense_data.amount is not None:
        expense["amount"] = expense_data.amount
    if expense_data.category is not None:
        expense["category"] = expense_data.category
    if expense_data.expense_date is not None:
        expense["expense_date"] = expense_data.expense_date
    if expense_data.notes is not None:
        expense["notes"] = expense_data.notes
    
    expenses_db[expense_id] = expense
    
    return ExpenseResponse(**expense)

@app.delete("/api/expenses/{expense_id}")
async def delete_expense(expense_id: int, current_user=Depends(get_current_user)):
    expense = expenses_db.get(expense_id)
    
    if not expense or expense["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    del expenses_db[expense_id]
    
    return {"message": "Expense deleted successfully"}

# Dashboard routes
@app.get("/api/dashboard/summary")
async def get_dashboard_summary(current_user=Depends(get_current_user)):
    user_expenses = [exp for exp in expenses_db.values() if exp["user_id"] == current_user["id"]]
    
    total_expenses = len(user_expenses)
    total_amount = sum(exp["amount"] for exp in user_expenses)
    
    # This month's expenses
    current_month = datetime.now().month
    current_year = datetime.now().year
    this_month_expenses = [
        exp for exp in user_expenses 
        if exp["expense_date"].month == current_month and exp["expense_date"].year == current_year
    ]
    this_month_amount = sum(exp["amount"] for exp in this_month_expenses)
    
    # Category breakdown
    categories = {}
    for exp in user_expenses:
        category = exp["category"]
        categories[category] = categories.get(category, 0) + exp["amount"]
    
    return {
        "total_expenses": total_expenses,
        "total_amount": total_amount,
        "this_month_amount": this_month_amount,
        "this_month_expenses": len(this_month_expenses),
        "categories": categories
    }

# ======= NEW ML-POWERED ENDPOINTS =======

# Simple categorization endpoint (no auth required for testing)
@app.post("/api/ai/categorize")
async def categorize_expense_endpoint(
    description: str,
    amount: Optional[float] = None
):
    """
    Simple AI categorization endpoint for frontend integration
    """
    try:
        if ML_ENHANCED:
            result = await categorize_expense_detailed(
                description=description,
                amount=amount,
                user_id=None  # No user context for public endpoint
            )
            return {
                "success": True,
                "category": result["category"],
                "confidence": result["confidence"],
                "method": result["method"]
            }
        else:
            # Fallback to basic categorization
            if AI_AVAILABLE:
                category = await categorize_expense_ai(description, amount)
            else:
                category = categorize_expense_rules(description)
            
            return {
                "success": True,
                "category": category,
                "confidence": 0.5,
                "method": "basic_ai" if AI_AVAILABLE else "rules"
            }
    
    except Exception as e:
        print(f"❌ Categorization error: {e}")
        return {
            "success": False,
            "category": "Other",
            "confidence": 0.1,
            "method": "error_fallback",
            "error": str(e)
        }

# Enhanced categorization endpoint
@app.post("/api/ai/categorize-smart")
async def smart_categorize_expense(
    description: str,
    amount: Optional[float] = None,
    current_user=Depends(get_current_user)
):
    """
    Enhanced ML-powered expense categorization with detailed results
    """
    try:
        if ML_ENHANCED:
            result = await categorize_expense_detailed(
                description=description,
                amount=amount,
                user_id=str(current_user["id"])
            )
            return {
                "success": True,
                "categorization": result,
                "ml_enhanced": True
            }
        else:
            # Fallback to basic AI
            if AI_AVAILABLE:
                category = await categorize_expense_ai(description, amount)
            else:
                category = categorize_expense_rules(description)
            
            return {
                "success": True,
                "categorization": {
                    "category": category,
                    "confidence": 0.5,
                    "method": "basic_ai" if AI_AVAILABLE else "rules",
                    "reasoning": "Basic categorization (ML enhancement unavailable)"
                },
                "ml_enhanced": False
            }
    
    except Exception as e:
        print(f"❌ Smart categorization error: {e}")
        return {
            "success": False,
            "error": str(e),
            "categorization": {
                "category": "Other",
                "confidence": 0.1,
                "method": "error_fallback",
                "reasoning": "Error occurred during categorization"
            }
        }

# Financial advice endpoint
@app.post("/api/ai/financial-advice")
async def get_user_financial_advice(
    advice_type: str = "general",
    include_profile: bool = False,
    current_user=Depends(get_current_user)
):
    """
    Generate personalized financial advice based on user's spending patterns
    """
    try:
        # Get user's expenses
        user_expenses = [
            {
                "description": exp["description"],
                "amount": exp["amount"],
                "category": exp["category"],
                "date": exp["expense_date"].isoformat() if hasattr(exp["expense_date"], 'isoformat') else str(exp["expense_date"])
            }
            for exp in expenses_db.values() 
            if exp["user_id"] == current_user["id"]
        ]
        
        # Basic user profile (can be enhanced with actual user data)
        user_profile = {
            "user_id": current_user["id"],
            "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()
        } if include_profile else None
        
        if ML_ENHANCED:
            advice = await get_financial_advice(
                expenses=user_expenses,
                user_profile=user_profile,
                advice_type=advice_type
            )
            
            return {
                "success": True,
                "advice": advice,
                "expense_count": len(user_expenses),
                "ml_enhanced": True
            }
        else:
            # Fallback advice
            return {
                "success": True,
                "advice": {
                    "advice_type": advice_type,
                    "main_advice": "Continue tracking your expenses to identify spending patterns and opportunities for improvement.",
                    "action_items": [
                        "Track all expenses consistently",
                        "Review spending weekly",
                        "Set up basic budget categories"
                    ],
                    "confidence": 0.3,
                    "processing_method": "basic_fallback"
                },
                "expense_count": len(user_expenses),
                "ml_enhanced": False
            }
    
    except Exception as e:
        print(f"❌ Financial advice error: {e}")
        return {
            "success": False,
            "error": str(e),
            "advice": {
                "main_advice": "Unable to generate personalized advice at this time. Continue tracking expenses for better insights.",
                "action_items": ["Keep tracking expenses"],
                "confidence": 0.1
            }
        }

# Spending insights endpoint
@app.get("/api/ai/spending-insights")
async def get_user_spending_insights(current_user=Depends(get_current_user)):
    """
    Get detailed spending insights and patterns for the user
    """
    try:
        # Get user's expenses with more detail
        user_expenses = []
        for exp in expenses_db.values():
            if exp["user_id"] == current_user["id"]:
                user_expenses.append({
                    "id": exp["id"],
                    "description": exp["description"],
                    "amount": exp["amount"],
                    "category": exp["category"],
                    "date": exp["expense_date"].isoformat() if hasattr(exp["expense_date"], 'isoformat') else str(exp["expense_date"]),
                    "notes": exp.get("notes", "")
                })
        
        if ML_ENHANCED:
            insights = await get_spending_insights(user_expenses)
            
            return {
                "success": True,
                "insights": insights,
                "expense_count": len(user_expenses),
                "ml_enhanced": True
            }
        else:
            # Basic insights fallback
            total_amount = sum(exp["amount"] for exp in user_expenses)
            categories = {}
            for exp in user_expenses:
                cat = exp["category"]
                categories[cat] = categories.get(cat, 0) + exp["amount"]
            
            return {
                "success": True,
                "insights": {
                    "total_spending": total_amount,
                    "category_breakdown": categories,
                    "expense_count": len(user_expenses),
                    "average_expense": total_amount / len(user_expenses) if user_expenses else 0,
                    "recommendations": [
                        "Continue tracking expenses for better insights",
                        "Review spending patterns monthly"
                    ]
                },
                "expense_count": len(user_expenses),
                "ml_enhanced": False
            }
    
    except Exception as e:
        print(f"❌ Spending insights error: {e}")
        return {
            "success": False,
            "error": str(e),
            "insights": {
                "error": "Unable to generate insights at this time"
            }
        }

# ML system status endpoint
@app.get("/api/ai/status")
async def get_ai_system_status():
    """
    Get the status of AI/ML systems
    """
    status = {
        "ai_available": AI_AVAILABLE,
        "ml_enhanced": ML_ENHANCED,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if ML_ENHANCED:
        try:
            # Get ML system statistics
            categorizer_stats = enhanced_categorizer.get_classification_stats()
            advisor_stats = financial_advisor.get_advice_stats()
            
            status.update({
                "categorization_stats": categorizer_stats,
                "advisor_stats": advisor_stats,
                "services": {
                    "enhanced_categorization": "available",
                    "financial_advisor": "available",
                    "spending_insights": "available"
                }
            })
        except Exception as e:
            status["error"] = f"Error getting ML stats: {e}"
    else:
        status["services"] = {
            "basic_categorization": "available" if AI_AVAILABLE else "unavailable",
            "financial_advisor": "unavailable",
            "spending_insights": "basic_only"
        }
    
    return status

# Batch operations endpoint
@app.post("/api/ai/batch-categorize")
async def batch_categorize_expenses(
    expense_descriptions: List[str],
    current_user=Depends(get_current_user)
):
    """
    Categorize multiple expenses efficiently
    """
    try:
        if not expense_descriptions:
            return {"success": False, "error": "No descriptions provided"}
        
        results = []
        
        if ML_ENHANCED:
            # Use enhanced batch processing
            expense_tuples = [(desc, 25.0) for desc in expense_descriptions]  # Default amount
            batch_results = enhanced_categorizer.batch_categorize(expense_tuples)
            
            for i, category in enumerate(batch_results):
                results.append({
                    "index": i,
                    "description": expense_descriptions[i],
                    "categorization": {
                        "category": category,
                        "confidence": 0.85,
                        "method": "enhanced_ml_batch"
                    }
                })
        else:
            # Basic categorization
            for i, description in enumerate(expense_descriptions):
                if AI_AVAILABLE:
                    category = await categorize_expense_ai(description)
                else:
                    category = categorize_expense_rules(description)
                
                results.append({
                    "index": i,
                    "description": description,
                    "categorization": {
                        "category": category,
                        "confidence": 0.5,
                        "method": "basic_batch"
                    }
                })
        
        return {
            "success": True,
            "results": results,
            "total_processed": len(results),
            "ml_enhanced": ML_ENHANCED
        }
    
    except Exception as e:
        print(f"❌ Batch categorization error: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
