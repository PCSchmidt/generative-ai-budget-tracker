# analytics_engine.py - Mock analytics engine for local development
import asyncio
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Mock analytics engine for local development"""
    
    def __init__(self, db_service=None):
        """Initialize mock analytics engine"""
        self.db_service = db_service
        logger.info("✅ Mock Analytics Engine initialized")
    
    async def generate_summary_analytics(self) -> Dict[str, Any]:
        """Generate summary analytics (mock implementation)"""
        
        # Get expenses from database if available
        expenses = []
        if self.db_service:
            try:
                expenses = await self.db_service.get_expenses()
            except Exception as e:
                logger.warning(f"Failed to get expenses: {e}")
        
        # Mock analytics data
        total_spending = sum(expense.get("amount", 0) for expense in expenses) if expenses else 153.38
        expense_count = len(expenses) if expenses else 5
        
        return {
            "total_spending": total_spending,
            "expense_count": expense_count,
            "average_confidence": 0.92,
            "top_categories": [
                {"category": "Food and Dining", "amount": 67.89, "percentage": 44.3},
                {"category": "Transportation", "amount": 45.50, "percentage": 29.7},
                {"category": "Entertainment", "amount": 39.99, "percentage": 26.0}
            ],
            "insights": [
                {
                    "type": "high_spending",
                    "category": "Food and Dining",
                    "message": "Food and Dining accounts for 44.3% of your spending ($67.89). Consider meal planning and bulk purchasing to optimize costs.",
                    "confidence": 0.90,
                    "priority": "medium"
                }
            ],
            "recommendations": [
                {
                    "title": "Optimize Food Spending",
                    "description": "Based on your patterns, meal planning could save you approximately $15.75 per month.",
                    "actions": ["Plan meals weekly", "Cook at home more often", "Use grocery lists"],
                    "potential_savings": 15.75
                }
            ],
            "ai_performance": {
                "total_categorizations": expense_count,
                "average_confidence": 0.92,
                "method_breakdown": {
                    "local_ai": 4,
                    "keyword": 1,
                    "manual": 0
                }
            },
            "generated_at": datetime.now().isoformat()
        }
    
    async def analyze_spending_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns (mock implementation)"""
        return {
            "patterns": [
                {
                    "pattern": "weekly_grocery_shopping",
                    "confidence": 0.85,
                    "description": "Regular grocery shopping pattern detected"
                }
            ],
            "trends": {
                "spending_trend": "increasing",
                "confidence": 0.78
            }
        }
    
    async def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect spending anomalies (mock implementation)"""
        return [
            {
                "type": "unusual_amount",
                "description": "Unusually high grocery spending",
                "confidence": 0.75,
                "severity": "medium"
            }
        ]
    
    async def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate financial insights (mock implementation)"""
        return [
            {
                "type": "category_optimization",
                "category": "Food and Dining",
                "insight": "Consider meal planning to reduce food expenses",
                "potential_savings": 15.75,
                "confidence": 0.88
            }
        ]
