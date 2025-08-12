from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category: Optional[str] = None
    expense_date: Optional[date] = None
    notes: Optional[str] = None

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
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseSummaryCategory(BaseModel):
    category: str
    total_amount: float
    count: int


class ExpenseSummaryResponse(BaseModel):
    total_amount: float
    count: int
    categories: List[ExpenseSummaryCategory]
    month: Optional[str] = None


class PaginatedExpensesResponse(BaseModel):
    items: List[ExpenseResponse]
    total: int
    page: int
    page_size: int
