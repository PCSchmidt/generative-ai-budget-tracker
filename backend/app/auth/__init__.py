"""
Authentication module for AI Budget Tracker
Provides JWT-based authentication with user management, email verification, and password reset
"""

from .models import auth_models
from .security import security
from .dependencies import get_current_user, get_current_verified_user, get_optional_user
from .routes import auth_router
from .schemas import UserResponse, TokenResponse

__all__ = [
    "auth_models",
    "security", 
    "get_current_user",
    "get_current_verified_user",
    "get_optional_user",
    "auth_router",
    "UserResponse",
    "TokenResponse"
]
