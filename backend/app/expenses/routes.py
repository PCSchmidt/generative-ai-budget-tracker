from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import func  # added

from app.database import get_db
from app.auth.models import Expense, Budget  # added Budget
from app.auth.dependencies import get_current_user
from .schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

@router.get('/', response_model=List[ExpenseResponse])
async def list_expenses(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    expenses = db.query(Expense).filter(Expense.user_id == current_user['id']).order_by(Expense.created_at.desc()).all()
    return expenses

# helper to recalc a budget's spent_amount for a given user & period (YYYY-MM)
def _recalc_budget(db: Session, user_id: int, period: str):
    budget = db.query(Budget).filter(Budget.user_id == user_id, Budget.period == period).first()
    if not budget:
        return
    total = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.user_id == user_id,
        Expense.expense_date.like(f"{period}-%")
    ).scalar() or 0
    budget.spent_amount = float(total)
    db.add(budget)

@router.post('/', response_model=ExpenseResponse)
async def create_expense(expense_data: ExpenseCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    new_expense = Expense(
        user_id=current_user['id'],
        description=expense_data.description,
        amount=expense_data.amount,
        category=expense_data.category or 'Other',
        expense_date=expense_data.expense_date or date.today(),
        notes=expense_data.notes
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    _recalc_budget(db, current_user['id'], new_expense.expense_date.strftime('%Y-%m'))
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get('/{expense_id}', response_model=ExpenseResponse)
async def get_expense(expense_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user['id']).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put('/{expense_id}', response_model=ExpenseResponse)
async def update_expense(expense_id: int, expense_data: ExpenseUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user['id']).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    old_period = expense.expense_date.strftime('%Y-%m') if expense.expense_date else None
    for field, value in expense_data.model_dump(exclude_none=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    new_period = expense.expense_date.strftime('%Y-%m') if expense.expense_date else None
    # Recalc old and new periods if changed
    periods = {p for p in [old_period, new_period] if p}
    for p in periods:
        _recalc_budget(db, current_user['id'], p)
    db.commit()
    db.refresh(expense)
    return expense

@router.delete('/{expense_id}')
async def delete_expense(expense_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user['id']).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    period = expense.expense_date.strftime('%Y-%m') if expense.expense_date else None
    db.delete(expense)
    db.commit()
    if period:
        _recalc_budget(db, current_user['id'], period)
        db.commit()
    return {"message": "Expense deleted successfully"}
