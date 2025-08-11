from datetime import datetime, timedelta, timezone
from typing import Optional
import os, secrets, hashlib, bcrypt
from jose import jwt
from sqlalchemy.orm import Session
from app.auth.models import RefreshToken

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

if os.getenv("TESTING") == "1":
    BCRYPT_ROUNDS = min(BCRYPT_ROUNDS, 4)

# Password hashing

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Access token

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_id": user_id, "exp": int(expire.timestamp())}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Refresh token helpers

def _generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)

def _hash_refresh(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_record(db: Session, user_id: int):
    raw = _generate_refresh_token()
    hashed = _hash_refresh(raw)
    expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(user_id=user_id, token_hash=hashed, expires_at=expires)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return raw, rt

def revoke_refresh_token(db: Session, rt: RefreshToken, replaced_by: Optional[int] = None):
    rt.revoked = True
    rt.replaced_by = replaced_by
    db.add(rt)
    db.commit()

__all__ = [
    'hash_password', 'verify_password', 'create_access_token', 'create_refresh_record', 'revoke_refresh_token', '_hash_refresh'
]
