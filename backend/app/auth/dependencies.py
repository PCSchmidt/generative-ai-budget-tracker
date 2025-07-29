"""
Authentication dependencies for AI Budget Tracker
FastAPI dependencies for protected routes and user authentication
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from .security import security
from .models import auth_models

logger = logging.getLogger(__name__)

# OAuth2 scheme for Swagger UI
security_scheme = HTTPBearer()

class AuthDependencies:
    """Authentication dependencies for FastAPI routes"""
    
    @staticmethod
    async def get_current_user(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
    ) -> Dict[str, Any]:
        """
        Dependency to get current authenticated user from JWT token
        Use this on protected routes: user = Depends(get_current_user)
        """
        try:
            # Extract token from Bearer authorization
            token = credentials.credentials
            
            # Verify the access token
            payload = security.verify_token(token, token_type="access")
            
            # Get user ID from token
            user_id = int(payload.get("sub"))
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: no user ID"
                )
            
            # Get user from database
            user = await auth_models.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Check if user is active
            if not user.get("is_active", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is deactivated"
                )
            
            logger.info(f"✅ Authenticated user: {user['email']} (ID: {user['id']})")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    @staticmethod
    async def get_current_verified_user(
        user: Dict[str, Any] = Depends(get_current_user.__func__)
    ) -> Dict[str, Any]:
        """
        Dependency to get current authenticated AND verified user
        Use this for routes that require email verification
        """
        if not user.get("is_verified", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required. Please check your email and verify your account."
            )
        
        return user
    
    @staticmethod
    async def get_optional_user(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
    ) -> Optional[Dict[str, Any]]:
        """
        Dependency to optionally get current user (don't fail if not authenticated)
        Use this for routes that work for both authenticated and anonymous users
        """
        if not credentials:
            return None
        
        try:
            return await AuthDependencies.get_current_user(request, credentials)
        except HTTPException:
            return None
    
    @staticmethod
    def get_request_info(request: Request) -> Dict[str, Any]:
        """
        Extract request information for session tracking
        """
        return {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "device_info": request.headers.get("x-device-info"),  # Custom header from frontend
        }

# Convenience dependencies for common use cases
get_current_user = AuthDependencies.get_current_user
get_current_verified_user = AuthDependencies.get_current_verified_user
get_optional_user = AuthDependencies.get_optional_user
get_request_info = AuthDependencies.get_request_info

# Rate limiting dependency (basic implementation)
class RateLimiter:
    """Simple rate limiter for authentication endpoints"""
    
    def __init__(self, requests_per_minute: int = 5):
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # In production, use Redis or similar
    
    async def __call__(self, request: Request):
        """Rate limit by IP address"""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if current_time - req_time < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in a minute."
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)

import time

# Rate limiters for different endpoints
auth_rate_limiter = RateLimiter(requests_per_minute=5)  # 5 auth attempts per minute
signup_rate_limiter = RateLimiter(requests_per_minute=3)  # 3 signups per minute
password_reset_rate_limiter = RateLimiter(requests_per_minute=2)  # 2 password resets per minute
