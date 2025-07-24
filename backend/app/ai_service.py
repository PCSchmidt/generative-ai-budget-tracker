"""
AI Service for Budget Tracker
Simple AI integration following Railway deployment patterns
"""

import os
import logging
from typing import Dict, List, Optional
import json

# Setup logging
logger = logging.getLogger(__name__)

class AIService:
    """Simple AI service for expense categorization and financial advice"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY") 
        self.hf_key = os.getenv("HUGGINGFACE_API_KEY")
        
    def categorize_expense(self, description: str, amount: float) -> Dict:
        """Categorize expense using simple rules (AI integration comes later)"""
        
        # Simple rule-based categorization for now
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['coffee', 'restaurant', 'food', 'grocery', 'starbucks', 'mcdonald']):
            category = "Food & Dining"
            confidence = 0.85
        elif any(word in description_lower for word in ['gas', 'fuel', 'uber', 'taxi', 'transport', 'bus']):
            category = "Transportation"
            confidence = 0.80
        elif any(word in description_lower for word in ['amazon', 'shopping', 'store', 'mall', 'retail']):
            category = "Shopping"
            confidence = 0.75
        elif any(word in description_lower for word in ['netflix', 'spotify', 'entertainment', 'movie', 'game']):
            category = "Entertainment"
            confidence = 0.70
        elif any(word in description_lower for word in ['electric', 'water', 'internet', 'phone', 'utility']):
            category = "Utilities"
            confidence = 0.85
        else:
            category = "Other"
            confidence = 0.50
            
        return {
            "category": category,
            "confidence": confidence,
            "ai_used": False,  # Will be True when we integrate real AI
            "fallback": "rule_based"
        }
    
    def generate_financial_advice(self, expenses: List[Dict], budget: Optional[Dict] = None) -> Dict:
        """Generate simple financial advice"""
        
        if not expenses:
            return {
                "advice": "Start tracking your expenses to get personalized insights!",
                "tips": ["Add your first expense to begin", "Set up a monthly budget"],
                "ai_used": False
            }
        
        total_spent = sum(exp.get('amount', 0) for exp in expenses)
        categories = {}
        
        for expense in expenses:
            cat = expense.get('category', 'Other')
            categories[cat] = categories.get(cat, 0) + expense.get('amount', 0)
        
        # Simple advice based on spending patterns
        top_category = max(categories.items(), key=lambda x: x[1]) if categories else None
        
        advice_parts = []
        if top_category:
            advice_parts.append(f"Your highest spending is in {top_category[0]} (${top_category[1]:.2f})")
        
        if total_spent > 0:
            advice_parts.append(f"Total tracked spending: ${total_spent:.2f}")
        
        return {
            "advice": ". ".join(advice_parts) if advice_parts else "Keep tracking to build spending insights!",
            "spending_breakdown": categories,
            "total_spent": total_spent,
            "ai_used": False,
            "tips": [
                "Consider setting category budgets",
                "Look for patterns in your top spending areas",
                "Track daily to build good habits"
            ]
        }
    
    def check_ai_status(self) -> Dict:
        """Check which AI services are available"""
        return {
            "openai_available": bool(self.openai_key),
            "groq_available": bool(self.groq_key),
            "huggingface_available": bool(self.hf_key),
            "current_mode": "rule_based",
            "upgrade_available": True
        }

# Global AI service instance
ai_service = AIService()

def get_ai_service():
    """Get AI service instance"""
    return ai_service
