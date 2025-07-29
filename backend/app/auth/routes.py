"""
Authentication routes for AI Budget Tracker
FastAPI routes for user signup, login, password reset, and profile management
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from .schemas import (
    UserSignupRequest, UserLoginRequest, UserResponse, TokenResponse,
    TokenRefreshRequest, PasswordResetRequest, PasswordResetConfirm,
    EmailVerificationRequest, UserUpdateRequest, PasswordChangeRequest,
    LogoutRequest, AuthStatusResponse, ErrorResponse
)
from .models import auth_models
from .security import security
from .dependencies import (
    get_current_user, get_current_verified_user, get_request_info,
    auth_rate_limiter, signup_rate_limiter, password_reset_rate_limiter
)

logger = logging.getLogger(__name__)

# Create authentication router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: Request,
    user_data: UserSignupRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(signup_rate_limiter)
):
    """
    Register a new user account
    - Creates user with email verification required
    - Sends verification email in background
    - Returns JWT tokens for immediate access
    """
    try:
        # Generate verification token
        verification_token = security.generate_verification_token()
        
        # Prepare user data for database
        user_dict = user_data.dict()
        user_dict["verification_token"] = verification_token
        
        # Create user in database
        created_user = await auth_models.create_user(user_dict)
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        # Generate token pair
        tokens = security.create_token_pair(created_user)
        
        # Create session in database
        request_info = get_request_info(request)
        session_data = security.generate_session_data(
            created_user["id"], 
            tokens["refresh_token"],
            request_info
        )
        
        refresh_token = await auth_models.create_session(session_data)
        if not refresh_token:
            logger.warning(f"Failed to create session for user {created_user['id']}")
        
        # Send verification email in background
        background_tasks.add_task(
            send_verification_email,
            created_user["email"],
            created_user["first_name"] or created_user["username"],
            verification_token
        )
        
        # Convert user for response
        user_response = UserResponse(**created_user)
        
        logger.info(f"✅ User registered: {created_user['email']} (ID: {created_user['id']})")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=user_response
        )
        
    except ValueError as e:
        # User validation errors (email exists, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Signup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@auth_router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: UserLoginRequest,
    _: None = Depends(auth_rate_limiter)
):
    """
    Authenticate user and return JWT tokens
    - Validates email and password
    - Creates new session
    - Returns access and refresh tokens
    """
    try:
        # Get user by email
        user = await auth_models.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not security.verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated. Please contact support."
            )
        
        # Generate token pair
        user_data = {k: v for k, v in user.items() if k != "hashed_password"}
        tokens = security.create_token_pair(user_data)
        
        # Create session in database
        request_info = get_request_info(request)
        session_data = security.generate_session_data(
            user["id"], 
            tokens["refresh_token"],
            request_info
        )
        
        refresh_token = await auth_models.create_session(session_data)
        if not refresh_token:
            logger.warning(f"Failed to create session for user {user['id']}")
        
        # Update last login
        await auth_models.update_user_login(user["id"])
        
        # Convert user for response (exclude password hash)
        user_response = UserResponse(**user_data)
        
        logger.info(f"✅ User logged in: {user['email']} (ID: {user['id']})")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    refresh_data: TokenRefreshRequest
):
    """
    Refresh access token using refresh token
    - Validates refresh token
    - Issues new access token
    - Optionally rotates refresh token
    """
    try:
        # Verify refresh token
        payload = security.verify_token(refresh_data.refresh_token, token_type="refresh")
        user_id = int(payload.get("sub"))
        
        # Get session from database
        session = await auth_models.get_session_by_token(refresh_data.refresh_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user data
        user = await auth_models.get_user_by_id(user_id)
        if not user or not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated"
            )
        
        # Generate new token pair
        tokens = security.create_token_pair(user)
        
        # Optionally rotate refresh token (for better security)
        request_info = get_request_info(request)
        session_data = security.generate_session_data(
            user["id"], 
            tokens["refresh_token"],
            request_info
        )
        
        # Delete old session and create new one
        await auth_models.delete_session(refresh_data.refresh_token)
        await auth_models.create_session(session_data)
        
        user_response = UserResponse(**user)
        
        logger.info(f"✅ Token refreshed for user: {user['email']} (ID: {user['id']})")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@auth_router.post("/logout")
async def logout(
    logout_data: LogoutRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Logout user by invalidating refresh token
    - Removes session from database
    - Client should discard access token
    """
    try:
        if logout_data.refresh_token:
            # Delete specific session
            deleted = await auth_models.delete_session(logout_data.refresh_token)
            if deleted:
                logger.info(f"✅ User logged out: {current_user['email']}")
                return {"message": "Logged out successfully"}
            else:
                logger.warning(f"Session not found for logout: {current_user['email']}")
                return {"message": "Session not found, but logged out"}
        else:
            return {"message": "No refresh token provided"}
            
    except Exception as e:
        logger.error(f"❌ Logout failed: {e}")
        # Don't fail logout even if there's an error
        return {"message": "Logged out (with errors)"}

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current user profile information
    - Returns user data without sensitive fields
    """
    return UserResponse(**current_user)

@auth_router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get authentication status
    - Returns whether user is authenticated and verified
    """
    return AuthStatusResponse(
        authenticated=True,
        user=UserResponse(**current_user),
        message=f"Authenticated as {current_user['email']}"
    )

@auth_router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest
):
    """
    Verify user email address
    - Uses verification token sent via email
    - Activates user account
    """
    try:
        verified = await auth_models.verify_user_email(verification_data.token)
        if verified:
            logger.info(f"✅ Email verified with token: {verification_data.token[:8]}...")
            return {"message": "Email verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Email verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

# Background task for sending verification email
async def send_verification_email(email: str, name: str, verification_token: str):
    """
    Background task to send verification email
    In production, integrate with email service (SendGrid, AWS SES, etc.)
    """
    try:
        # For now, just log the verification token
        logger.info(f"📧 Email verification token for {email}: {verification_token}")
        logger.info(f"🔗 Verification URL: /auth/verify-email?token={verification_token}")
        
        # TODO: Implement actual email sending
        # await email_service.send_verification_email(email, name, verification_token)
        
    except Exception as e:
        logger.error(f"❌ Failed to send verification email: {e}")

# Additional routes for password reset (will implement next)
@auth_router.post("/forgot-password")
async def forgot_password(
    request: Request,
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(password_reset_rate_limiter)
):
    """
    Request password reset
    - Sends reset token via email
    - Rate limited to prevent abuse
    """
    try:
        user = await auth_models.get_user_by_email(reset_data.email)
        if user:
            # Generate reset token
            reset_token = security.generate_reset_token()
            
            # TODO: Store reset token in database with expiration
            # await auth_models.create_password_reset_token(user["id"], reset_token)
            
            # Send reset email in background
            background_tasks.add_task(
                send_password_reset_email,
                user["email"],
                user["first_name"] or user["username"],
                reset_token
            )
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception as e:
        logger.error(f"❌ Password reset request failed: {e}")
        # Still return success to prevent information leakage
        return {"message": "If the email exists, a password reset link has been sent"}

async def send_password_reset_email(email: str, name: str, reset_token: str):
    """
    Background task to send password reset email
    """
    try:
        logger.info(f"📧 Password reset token for {email}: {reset_token}")
        logger.info(f"🔗 Reset URL: /auth/reset-password?token={reset_token}")
        
        # TODO: Implement actual email sending
        
    except Exception as e:
        logger.error(f"❌ Failed to send password reset email: {e}")
