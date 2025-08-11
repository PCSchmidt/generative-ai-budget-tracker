from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app.auth.models import User, RefreshToken
from .security import (
    hash_password, verify_password, create_access_token,
    create_refresh_record, revoke_refresh_token, _hash_refresh
)
from .schemas import (
    UserSignup, UserLogin, RefreshRequest, LogoutRequest,
    UserResponse, AuthPairResponse
)

security = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")

router = APIRouter(prefix="/auth", tags=["auth"])

# Optional rate limiter integration (limiter defined in main or elsewhere)
try:
    from slowapi import Limiter  # type: ignore
    from slowapi.util import get_remote_address  # type: ignore
    from fastapi import Request  # for key func usage
except ImportError:  # pragma: no cover
    Limiter = None  # type: ignore

# Endpoints
@router.post('/signup', response_model=AuthPairResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_data.email.lower(),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access = create_access_token(user.id)
    refresh_raw, _ = create_refresh_record(db, user.id)
    return AuthPairResponse(
        access_token=access,
        refresh_token=refresh_raw,
        user=UserResponse(id=user.id, email=user.email, first_name=user.first_name or "", last_name=user.last_name or "")
    )

@router.post('/login', response_model=AuthPairResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access = create_access_token(user.id)
    refresh_raw, _ = create_refresh_record(db, user.id)
    return AuthPairResponse(
        access_token=access,
        refresh_token=refresh_raw,
        user=UserResponse(id=user.id, email=user.email, first_name=user.first_name or "", last_name=user.last_name or "")
    )

@router.post('/refresh', response_model=AuthPairResponse)
async def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    hashed = _hash_refresh(req.refresh_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == hashed).first()
    now = datetime.now(timezone.utc)
    if (not rt) or rt.revoked or (rt.expires_at and (rt.expires_at.tzinfo and rt.expires_at < now or (rt.expires_at.tzinfo is None and rt.expires_at.replace(tzinfo=timezone.utc) < now))):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = db.query(User).filter(User.id == rt.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    new_raw, new_rt = create_refresh_record(db, user.id)
    revoke_refresh_token(db, rt, replaced_by=new_rt.id)
    access = create_access_token(user.id)
    return AuthPairResponse(
        access_token=access,
        refresh_token=new_raw,
        user=UserResponse(id=user.id, email=user.email, first_name=user.first_name or "", last_name=user.last_name or "")
    )

@router.post('/logout')
async def logout(req: LogoutRequest, db: Session = Depends(get_db)):
    hashed = _hash_refresh(req.refresh_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == hashed).first()
    if rt and not rt.revoked:
        revoke_refresh_token(db, rt)
    return {"success": True}

@router.get('/me', response_model=UserResponse)
async def me(credentials: HTTPAuthorizationCredentials | None = Depends(security), db: Session = Depends(get_db)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get('user_id')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return UserResponse(id=user.id, email=user.email, first_name=user.first_name or "", last_name=user.last_name or "")
