# database_service.py - Mock database service for local development
import asyncio
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Mock database service for local development"""
    
    def __init__(self):
        """Initialize mock database service"""
        self.expenses = []  # Mock storage
        self._next_id = 1
        logger.info("✅ Mock Database Service initialized")
    
    async def create_expense(
        self, 
        description: str, 
        amount: float, 
        category: str, 
        date: date,
        ai_confidence: Optional[float] = None,
        ai_method: Optional[str] = None
    ) -> int:
        """Create a new expense (mock implementation)"""
        expense = {
            "id": self._next_id,
            "description": description,
            "amount": amount,
            "category": category,
            "date": date.isoformat(),
            "ai_confidence": ai_confidence,
            "ai_method": ai_method,
            "created_at": datetime.now().isoformat()
        }
        
        self.expenses.append(expense)
        expense_id = self._next_id
        self._next_id += 1
        
        logger.info(f"Created expense: {description} - ${amount} ({category})")
        return expense_id
    
    async def get_expenses(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get expenses (mock implementation)"""
        return self.expenses[-limit:]
    
    async def get_expense_by_id(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """Get expense by ID (mock implementation)"""
        for expense in self.expenses:
            if expense["id"] == expense_id:
                return expense
        return None
    
    async def update_expense(self, expense_id: int, **updates) -> bool:
        """Update expense (mock implementation)"""
        for expense in self.expenses:
            if expense["id"] == expense_id:
                expense.update(updates)
                return True
        return False
    
    async def delete_expense(self, expense_id: int) -> bool:
        """Delete expense (mock implementation)"""
        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        return True
