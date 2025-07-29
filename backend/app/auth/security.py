"""
Security utilities for AI Budget Tracker
JWT token handling, password hashing, and security functions
"""

import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
import bcrypt
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Handles JWT tokens, password hashing, and security operations"""
    
    def __init__(self):
        # JWT Configuration
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-super-secure-jwt-secret-key-change-this")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        
        # Token expiration times
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # Warn if using default secret
        if self.secret_key == "your-super-secure-jwt-secret-key-change-this":
            logger.warning("⚠️ Using default JWT secret key! Change JWT_SECRET_KEY in production!")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"❌ Password verification failed: {e}")
            return False
    
    def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user_data["id"]),  # Subject (user ID)
            "email": user_data["email"],
            "username": user_data["username"],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": str(user_data["id"]),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    def generate_verification_token(self) -> str:
        """Generate a secure verification token for email verification"""
        # Generate a random string for email verification
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def generate_reset_token(self) -> str:
        """Generate a secure reset token for password reset"""
        # Generate a random string for password reset
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(48))
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create access and refresh token pair"""
        access_token = self.generate_access_token(user_data)
        refresh_token = self.generate_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60  # Convert to seconds
        }
    
    def get_token_expiry_datetime(self, days: Optional[int] = None) -> datetime:
        """Get expiry datetime for tokens"""
        if days:
            return datetime.utcnow() + timedelta(days=days)
        return datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength and return detailed feedback"""
        feedback = {
            "valid": True,
            "score": 0,
            "feedback": [],
            "requirements_met": {
                "min_length": False,
                "has_letter": False,
                "has_number": False,
                "has_uppercase": False,
                "has_lowercase": False,
                "has_special": False
            }
        }
        
        # Check minimum length
        if len(password) >= 8:
            feedback["requirements_met"]["min_length"] = True
            feedback["score"] += 1
        else:
            feedback["valid"] = False
            feedback["feedback"].append("Password must be at least 8 characters long")
        
        # Check for letters
        if any(c.isalpha() for c in password):
            feedback["requirements_met"]["has_letter"] = True
            feedback["score"] += 1
        else:
            feedback["valid"] = False
            feedback["feedback"].append("Password must contain at least one letter")
        
        # Check for numbers
        if any(c.isdigit() for c in password):
            feedback["requirements_met"]["has_number"] = True
            feedback["score"] += 1
        else:
            feedback["valid"] = False
            feedback["feedback"].append("Password must contain at least one number")
        
        # Check for uppercase
        if any(c.isupper() for c in password):
            feedback["requirements_met"]["has_uppercase"] = True
            feedback["score"] += 1
        else:
            feedback["feedback"].append("Consider adding uppercase letters for stronger security")
        
        # Check for lowercase
        if any(c.islower() for c in password):
            feedback["requirements_met"]["has_lowercase"] = True
            feedback["score"] += 1
        else:
            feedback["feedback"].append("Consider adding lowercase letters for stronger security")
        
        # Check for special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in password):
            feedback["requirements_met"]["has_special"] = True
            feedback["score"] += 1
        else:
            feedback["feedback"].append("Consider adding special characters for stronger security")
        
        # Length bonus
        if len(password) >= 12:
            feedback["score"] += 1
        
        return feedback
    
    def generate_session_data(self, user_id: int, refresh_token: str, 
                            request_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate session data for database storage"""
        session_data = {
            "user_id": user_id,
            "refresh_token": refresh_token,
            "expires_at": self.get_token_expiry_datetime(),
        }
        
        if request_info:
            session_data.update({
                "device_info": request_info.get("device_info"),
                "ip_address": request_info.get("ip_address"),
                "user_agent": request_info.get("user_agent"),
            })
        
        return session_data

# Global security manager instance
security = SecurityManager()
