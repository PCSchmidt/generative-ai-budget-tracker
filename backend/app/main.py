"""
AI Budget Tracker FastAPI Backend
Phase 2: Core Integration Backend (Refactored for modular auth & expenses)
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime, date, timezone, timedelta
from jose import jwt
import bcrypt
import os
import re
from pathlib import Path
import sys
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.models import User, Expense, RefreshToken

# Import modular routers
from app.auth.routes import router as auth_router
from app.expenses.routes import router as expenses_router
from app.budgets.routes import router as budgets_router
from app.goals.routes import router as goals_router
from app.auth.dependencies import get_current_user

# Add text for raw SQL in health
from sqlalchemy import text
from fastapi.responses import JSONResponse
from app.logging_config import setup_logging
import logging, json, uuid, time
import threading
from collections import OrderedDict

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # Go up one level to backend
sys.path.insert(0, current_dir)
sys.path.insert(0, backend_dir)

# Database setup
from app.database import Base, engine
from sqlalchemy.exc import SQLAlchemyError

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

# Record application start time for uptime calculation (timezone-aware)
APP_START_TIME = datetime.now(timezone.utc)

# Create FastAPI app
app = FastAPI(
    title="AI Budget Tracker API",
    description="Backend API for AI-powered expense tracking",
    version="2.0.0"
)

# Request ID middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.time()
    # attach to state
    request.state.request_id = req_id
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.time() - start) * 1000.0
        status_code = response.status_code if response else 500
        user_id = getattr(request.state, "user_id", None)
        log_record = {
            "event": "http_access",
            "request_id": req_id,
            "method": request.method,
            "path": request.url.path,
            "status": status_code,
            "duration_ms": round(duration_ms, 2),
            "user_id": user_id,
        }
        logger.info(json.dumps(log_record))
        if response:
            response.headers["X-Request-ID"] = req_id

# CORS middleware for frontend integration
# Configurable CORS for frontend integration (supports comma-separated list)
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
]
_env_origins = os.getenv("FRONTEND_ORIGINS", "").strip()
_origin_regex = os.getenv("FRONTEND_ORIGIN_REGEX", "").strip()
if _env_origins:
    try:
        allow_origins = [o.strip() for o in _env_origins.split(",") if o.strip()]
    except Exception:
        allow_origins = _default_origins
else:
    allow_origins = _default_origins

if _origin_regex:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Security
security = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DEFAULT_SECRET_PLACEHOLDER = "your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
# Configurable bcrypt rounds (default 12; lower in tests)
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
if os.getenv("TESTING") == "1":
    BCRYPT_ROUNDS = min(BCRYPT_ROUNDS, 4)
if SECRET_KEY == DEFAULT_SECRET_PLACEHOLDER or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECURITY ERROR: SECRET_KEY is unset, default, or too short (<32 chars). Set a strong SECRET_KEY env var before starting the app."
    )

# Utility functions (defined early for use in test data)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Replace create_access_token with env-configured expiry & timezone-aware

def _utc_now():
    return datetime.now(timezone.utc)

def _coerce_utc(dt: datetime | None):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_id": user_id, "exp": int(expire.timestamp())}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Remove automatic metadata.create_all bootstrap to enforce Alembic migrations
# (Was previously here). If you attempt to use legacy ALLOW_BOOTSTRAP, fail fast with guidance.
if os.getenv("ALLOW_BOOTSTRAP") == "1":
    raise RuntimeError(
        "Deprecated: ALLOW_BOOTSTRAP path removed. Use Alembic migrations instead (run 'alembic upgrade head') and unset ALLOW_BOOTSTRAP."
    )

# Pydantic models
class UserSignup(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # Password policy: min 8 chars, at least 1 upper, 1 lower, 1 digit
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must include an uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must include a lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must include a digit')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
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

class AuthPairResponse(TokenResponse):
    refresh_token: str | None = None

# Initialize logging
setup_logging()
logger = logging.getLogger("access")
security_logger = logging.getLogger("security")
ai_logger = logging.getLogger("ai")

# (Remove old auth helpers and endpoints; rely on auth_router & expenses_router now)
# Keep AI categorization, dashboard, cache endpoints.

# Include routers
app.include_router(auth_router)
app.include_router(expenses_router)
app.include_router(budgets_router)
app.include_router(goals_router)

# ======= SIMPLE IN-MEMORY TTL CACHE (AI RESULTS) =======
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 min default
CACHE_MAX_ITEMS = int(os.getenv("CACHE_MAX_ITEMS", "500"))

class _TTLCache:
    def __init__(self, max_items: int, ttl_seconds: int):
        self.store: OrderedDict[str, tuple] = OrderedDict()
        self.max_items = max_items
        self.ttl = ttl_seconds
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _purge_expired(self):
        now = time.time()
        expired_keys = [k for k, (_, ts) in self.store.items() if now - ts > self.ttl]
        for k in expired_keys:
            self.store.pop(k, None)

    def get(self, key: str):
        with self.lock:
            self._purge_expired()
            if key in self.store:
                value, ts = self.store[key]
                if time.time() - ts <= self.ttl:
                    # move to end (recently used)
                    self.store.move_to_end(key)
                    self.hits += 1
                    return value
                else:
                    self.store.pop(key, None)
            self.misses += 1
            return None

    def set(self, key: str, value):
        with self.lock:
            if key in self.store:
                self.store.move_to_end(key)
            self.store[key] = (value, time.time())
            if len(self.store) > self.max_items:
                # evict oldest
                self.store.popitem(last=False)
                self.evictions += 1

    def stats(self):
        with self.lock:
            return {
                "items": len(self.store),
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "hit_rate": round(self.hits / (self.hits + self.misses), 3) if (self.hits + self.misses) else 0.0,
                "ttl_seconds": self.ttl,
                "max_items": self.max_items,
            }

_ai_cache = _TTLCache(CACHE_MAX_ITEMS, CACHE_TTL_SECONDS)

def _norm_desc(desc: str) -> str:
    return (desc or "").strip().lower()

def _cat_key(description: str, amount: float, user_id: str | None) -> str:
    amt_bucket = None if amount is None else round(float(amount), 2)
    return f"cat|{user_id or 'anon'}|{_norm_desc(description)}|{amt_bucket}"

def _advice_key(expense_count: int, total_amount: float, user_id: str | None, advice_type: str) -> str:
    return f"advice|{user_id or 'anon'}|{advice_type}|{expense_count}|{round(total_amount,2)}"

def _insights_key(expense_count: int, total_amount: float, user_id: str | None) -> str:
    return f"insights|{user_id or 'anon'}|{expense_count}|{round(total_amount,2)}"

# Public stats endpoint (optional; lightweight)
@app.get("/api/cache/stats")
async def cache_stats():
    return {"cache": _ai_cache.stats()}

# Wrapper helpers used by endpoints
async def cached_categorize(description: str, amount: float | None, user_id: str | None):
    key = _cat_key(description, amount, user_id)
    cached = _ai_cache.get(key)
    if cached is not None:
        ai_logger.debug(f"cache_hit categorization key={key}")
        return cached
    ai_logger.debug(f"cache_miss categorization key={key}")
    # Delegate to existing detailed function (handles ML/fallback)
    result = await categorize_expense_detailed(description=description, amount=amount, user_id=user_id)
    _ai_cache.set(key, result)
    return result

async def cached_financial_advice(expenses: list, user_id: str | None, advice_type: str):
    total_amount = sum(e.get("amount", 0) for e in expenses)
    key = _advice_key(len(expenses), total_amount, user_id, advice_type)
    cached = _ai_cache.get(key)
    if cached is not None:
        ai_logger.debug(f"cache_hit advice key={key}")
        return cached
    ai_logger.debug(f"cache_miss advice key={key}")
    result = await get_financial_advice(expenses=expenses, user_profile=None, advice_type=advice_type)
    _ai_cache.set(key, result)
    return result

async def cached_spending_insights(expenses: list, user_id: str | None):
    total_amount = sum(e.get("amount", 0) for e in expenses)
    key = _insights_key(len(expenses), total_amount, user_id)
    cached = _ai_cache.get(key)
    if cached is not None:
        ai_logger.debug(f"cache_hit insights key={key}")
        return cached
    ai_logger.debug(f"cache_miss insights key={key}")
    result = await get_spending_insights(expenses)
    _ai_cache.set(key, result)
    return result

# Routes
@app.get("/")
async def root():
    return {"message": "AI Budget Tracker API", "version": "2.0.0", "status": "running"}

# Lightweight readiness probe that always returns 200 once the app is started
@app.get("/ready")
async def ready():
    return {
        "ok": True,
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check including DB, AI subsystem status, migration revision, and uptime."""
    db_ok = False
    db_error = None
    alembic_rev = None
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
        # Attempt to read alembic revision
        try:
            result = db.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            row = result.first()
            if row:
                alembic_rev = row[0]
        except Exception:
            # alembic_version table may not exist yet
            alembic_rev = None
    except SQLAlchemyError as e:
        db_error = str(e)

    uptime_seconds = (datetime.now(timezone.utc) - APP_START_TIME).total_seconds()

    return {
        "status": "healthy" if db_ok else "degraded",
        "version": "2.0.0",
        "db": {"ok": db_ok, "error": db_error, "alembic_revision": alembic_rev},
        "ai": {"ai_available": 'AI_AVAILABLE' in globals() and AI_AVAILABLE, "ml_enhanced": 'ML_ENHANCED' in globals() and ML_ENHANCED},
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

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
            "timestamp": datetime.now(timezone.utc),
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

# ======= NEW ML-POWERED ENDPOINTS =======

# Simple categorization endpoint (no auth required for testing)
@app.post("/api/ai/categorize")
async def categorize_expense_endpoint(
    description: str,
    amount: Optional[float] = None,
    request: Request = None
):
    """
    Simple AI categorization endpoint for frontend integration
    """
    try:
        if ML_ENHANCED:
            result = await cached_categorize(description=description, amount=amount, user_id=None)
            return {
                "success": True,
                "category": result["category"],
                "confidence": result["confidence"],
                "method": result["method"],
                "cache": True  # indicate caching path used (hit or miss not distinguished here)
            }
        else:
            # Fallback to basic categorization (no caching since lightweight)
            if AI_AVAILABLE:
                category = await categorize_expense_ai(description, amount)
            else:
                category = categorize_expense_rules(description)
            return {
                "success": True,
                "category": category,
                "confidence": 0.5,
                "method": "basic_ai" if AI_AVAILABLE else "rules",
                "cache": False
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
    current_user=Depends(get_current_user),
    request: Request = None
):
    """
    Enhanced ML-powered expense categorization with detailed results
    """
    try:
        if ML_ENHANCED:
            result = await cached_categorize(description=description, amount=amount, user_id=str(current_user["id"]))
            return {
                "success": True,
                "categorization": result,
                "ml_enhanced": True,
                "cache": True
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
                "ml_enhanced": False,
                "cache": False
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
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Generate personalized financial advice based on user's spending patterns
    """
    try:
        # Get user's expenses
        user_expenses = [
            {
                "description": e.description,
                "amount": e.amount,
                "category": e.category or "Other",
                "date": e.expense_date.isoformat()
            }
            for e in db.query(Expense).filter(Expense.user_id == current_user["id"]).all()
        ]
        
        # Basic user profile (can be enhanced with actual user data)
        user_profile = {
            "user_id": current_user["id"],
            "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()
        } if include_profile else None
        
        if ML_ENHANCED:
            advice = await cached_financial_advice(expenses=user_expenses, user_id=str(current_user["id"]), advice_type=advice_type)
            return {
                "success": True,
                "advice": advice,
                "expense_count": len(user_expenses),
                "ml_enhanced": True,
                "cache": True
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
                "ml_enhanced": False,
                "cache": False
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
async def get_user_spending_insights(request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get detailed spending insights and patterns for the user
    """
    try:
        # Get user's expenses with more detail
        user_expenses = [
            {
                "id": e.id,
                "description": e.description,
                "amount": e.amount,
                "category": e.category or "Other",
                "date": e.expense_date.isoformat(),
                "notes": e.notes or ""
            }
            for e in db.query(Expense).filter(Expense.user_id == current_user["id"]).all()
        ]
        
        if ML_ENHANCED:
            insights = await cached_spending_insights(user_expenses, user_id=str(current_user["id"]))
            return {
                "success": True,
                "insights": insights,
                "expense_count": len(user_expenses),
                "ml_enhanced": True,
                "cache": True
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
                "ml_enhanced": False,
                "cache": False
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
        "timestamp": datetime.now(timezone.utc).isoformat()
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
    request: Request,
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

# Define categorize_expense wrapper only if underlying function exists
async def categorize_expense(description: str, amount: float = None):
    try:
        return await categorize_expense_ai(description, amount)  # type: ignore
    except Exception:
        return categorize_expense_rules(description)  # type: ignore

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
except ImportError:
    Limiter = None  # type: ignore
    get_remote_address = None  # type: ignore

# Rate limiter setup remains; adjust wrapping to only wrap endpoints that exist locally now
if Limiter and get_remote_address:
    limiter = Limiter(key_func=get_remote_address, default_limits=["300/hour"])  # redefine after refactor
else:
    limiter = None

# After all route definitions, configure rate limiting decorators and handlers if limiter available
if limiter:
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        req_id = getattr(request.state, 'request_id', None)
        security_logger.warning(json.dumps({
            "event": "rate_limit_exceeded",
            "request_id": req_id,
            "path": request.url.path,
            "remote_addr": request.client.host if request.client else None,
            "detail": str(exc)
        }))
        return JSONResponse(status_code=429, content={
            "detail": "Rate limit exceeded",
            "request_id": req_id
        })
    # Only apply to AI endpoints retained here
    categorize_expense_endpoint = limiter.limit("30/minute")(categorize_expense_endpoint)
    smart_categorize_expense = limiter.limit("100/hour")(smart_categorize_expense)
    get_user_financial_advice = limiter.limit("100/hour")(get_user_financial_advice)
    get_user_spending_insights = limiter.limit("100/hour")(get_user_spending_insights)
    batch_categorize_expenses = limiter.limit("100/hour")(batch_categorize_expenses)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
