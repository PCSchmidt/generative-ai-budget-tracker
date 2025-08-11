from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.database import get_db
from app.auth.models import Budget, Expense
from app.auth.dependencies import get_current_user
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix='/api/budgets', tags=['budgets'])

class BudgetCreate(BaseModel):
    period: str  # YYYY-MM
    total_limit: float
    notes: str | None = None

class BudgetUpdate(BaseModel):
    total_limit: float | None = None
    notes: str | None = None

class BudgetResponse(BaseModel):
    id: int
    period: str
    total_limit: float
    spent_amount: float
    remaining: float
    utilization: float
    notes: str | None

    model_config = ConfigDict(from_attributes=True)

@router.get('/', response_model=List[BudgetResponse])
async def list_budgets(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Budget).filter(Budget.user_id == current_user['id']).order_by(Budget.period.desc()).all()
    resp = []
    for b in items:
        remaining = max(b.total_limit - (b.spent_amount or 0), 0)
        util = (b.spent_amount / b.total_limit) if b.total_limit else 0
        resp.append(BudgetResponse(id=b.id, period=b.period, total_limit=b.total_limit, spent_amount=b.spent_amount or 0, remaining=remaining, utilization=round(util, 4), notes=b.notes))
    return resp

@router.post('/', response_model=BudgetResponse)
async def create_budget(data: BudgetCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Compute current spent for that period from expenses
    existing = db.query(Budget).filter(Budget.user_id==current_user['id'], Budget.period==data.period).first()
    if existing:
        raise HTTPException(status_code=400, detail='Budget for period already exists')
    # Aggregate expenses for period (YYYY-MM prefix)
    spent = db.query(Expense).filter(Expense.user_id==current_user['id']).filter(Expense.expense_date.like(f"{data.period}-%")).with_entities(func.coalesce(func.sum(Expense.amount),0)).scalar()  # type: ignore
    b = Budget(user_id=current_user['id'], period=data.period, total_limit=data.total_limit, spent_amount=spent or 0, notes=data.notes)
    db.add(b)
    db.commit()
    db.refresh(b)
    remaining = max(b.total_limit - (b.spent_amount or 0), 0)
    util = (b.spent_amount / b.total_limit) if b.total_limit else 0
    return BudgetResponse(id=b.id, period=b.period, total_limit=b.total_limit, spent_amount=b.spent_amount or 0, remaining=remaining, utilization=round(util,4), notes=b.notes)

@router.put('/{budget_id}', response_model=BudgetResponse)
async def update_budget(budget_id: int, data: BudgetUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(Budget).filter(Budget.id==budget_id, Budget.user_id==current_user['id']).first()
    if not b:
        raise HTTPException(status_code=404, detail='Budget not found')
    if data.total_limit is not None:
        b.total_limit = data.total_limit
    if data.notes is not None:
        b.notes = data.notes
    db.commit()
    db.refresh(b)
    remaining = max(b.total_limit - (b.spent_amount or 0), 0)
    util = (b.spent_amount / b.total_limit) if b.total_limit else 0
    return BudgetResponse(id=b.id, period=b.period, total_limit=b.total_limit, spent_amount=b.spent_amount or 0, remaining=remaining, utilization=round(util,4), notes=b.notes)

@router.delete('/{budget_id}')
async def delete_budget(budget_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(Budget).filter(Budget.id==budget_id, Budget.user_id==current_user['id']).first()
    if not b:
        raise HTTPException(status_code=404, detail='Budget not found')
    db.delete(b)
    db.commit()
    return {'success': True}
