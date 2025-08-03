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
from app.ai_categorizer import categorize_expense_ai, categorize_expense_rules

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

# Test AI categorization endpoint
@app.post("/api/categorize-test")
async def test_categorization(description: str, amount: float = None):
    """Test endpoint for AI expense categorization"""
    try:
        category = await categorize_expense(description, amount)
        return {
            "description": description,
            "amount": amount,
            "predicted_category": category,
            "method": "AI with rule-based fallback",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "error": str(e),
            "description": description,
            "fallback_category": categorize_expense_sync(description)
        }

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
    
    # Auto-categorize if no category provided using AI
    if expense_data.category:
        category = expense_data.category
    else:
        category = await categorize_expense(expense_data.description, expense_data.amount)
    
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
        "created_at": datetime.utcnow()
    }
    
    expenses_db[expense_id] = expense
    
    return ExpenseResponse(**expense)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
