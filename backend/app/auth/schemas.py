from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import date, datetime
import re

# Existing user/expense schemas (retained)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)

class ExpenseBase(BaseModel):
    description: str
    amount: float
    category: Optional[str] = None
    expense_date: Optional[date] = None
    notes: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseRead(BaseModel):
    id: int
    description: str
    amount: float
    category: Optional[str] = None
    expense_date: date
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# New auth schemas consolidated here
class UserSignup(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

    @field_validator('password')
    @classmethod
    def password_policy(cls, v):
        if len(v) < 8 or not re.search(r'[A-Z]', v) or not re.search(r'[a-z]', v) or not re.search(r'[0-9]', v):
            raise ValueError('Weak password')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str

class AuthPairResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    user: UserResponse
