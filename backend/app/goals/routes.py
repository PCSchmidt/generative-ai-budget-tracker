from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from pydantic import BaseModel, ConfigDict, field_validator
from app.database import get_db
from app.auth.models import Goal, Expense
from app.auth.dependencies import get_current_user
from sqlalchemy import func

router = APIRouter(prefix='/api/goals', tags=['goals'])

class GoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: date | None = None
    notes: str | None = None

    @field_validator('target_amount')
    @classmethod
    def positive_amount(cls, v):
        if v <= 0:
            raise ValueError('target_amount must be positive')
        return v

class GoalUpdate(BaseModel):
    name: str | None = None
    target_amount: float | None = None
    current_amount: float | None = None
    target_date: date | None = None
    notes: str | None = None

class GoalResponse(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    progress_percent: float
    target_date: date | None
    notes: str | None

    model_config = ConfigDict(from_attributes=True)

@router.get('/', response_model=List[GoalResponse])
async def list_goals(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.query(Goal).filter(Goal.user_id == current_user['id']).order_by(Goal.created_at.desc()).all()
    resp: list[GoalResponse] = []
    for g in goals:
        pct = (g.current_amount / g.target_amount) if g.target_amount else 0
        resp.append(GoalResponse(id=g.id, name=g.name, target_amount=g.target_amount, current_amount=g.current_amount, progress_percent=round(pct*100,2), target_date=g.target_date, notes=g.notes))
    return resp

@router.post('/', response_model=GoalResponse)
async def create_goal(data: GoalCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    g = Goal(user_id=current_user['id'], name=data.name, target_amount=data.target_amount, current_amount=0, target_date=data.target_date, notes=data.notes)
    db.add(g)
    db.commit()
    db.refresh(g)
    return GoalResponse(id=g.id, name=g.name, target_amount=g.target_amount, current_amount=g.current_amount, progress_percent=0.0, target_date=g.target_date, notes=g.notes)

@router.put('/{goal_id}', response_model=GoalResponse)
async def update_goal(goal_id: int, data: GoalUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    g = db.query(Goal).filter(Goal.id==goal_id, Goal.user_id==current_user['id']).first()
    if not g:
        raise HTTPException(status_code=404, detail='Goal not found')
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(g, field, value)
    db.commit()
    db.refresh(g)
    pct = (g.current_amount / g.target_amount) if g.target_amount else 0
    return GoalResponse(id=g.id, name=g.name, target_amount=g.target_amount, current_amount=g.current_amount, progress_percent=round(pct*100,2), target_date=g.target_date, notes=g.notes)

@router.delete('/{goal_id}')
async def delete_goal(goal_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    g = db.query(Goal).filter(Goal.id==goal_id, Goal.user_id==current_user['id']).first()
    if not g:
        raise HTTPException(status_code=404, detail='Goal not found')
    db.delete(g)
    db.commit()
    return {'success': True}

@router.post('/{goal_id}/contribute', response_model=GoalResponse)
async def contribute_to_goal(goal_id: int, amount: float, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail='Contribution must be positive')
    g = db.query(Goal).filter(Goal.id==goal_id, Goal.user_id==current_user['id']).first()
    if not g:
        raise HTTPException(status_code=404, detail='Goal not found')
    g.current_amount = float(g.current_amount or 0) + amount
    if g.target_amount and g.current_amount > g.target_amount:
        g.current_amount = g.target_amount  # hard cap
    db.commit()
    db.refresh(g)
    pct = (g.current_amount / g.target_amount) if g.target_amount else 0
    return GoalResponse(id=g.id, name=g.name, target_amount=g.target_amount, current_amount=g.current_amount, progress_percent=round(pct*100,2), target_date=g.target_date, notes=g.notes)
