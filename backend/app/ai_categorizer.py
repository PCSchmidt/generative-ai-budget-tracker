"""
AI Expense Categorization Service
Uses Hugging Face models for intelligent expense categorization
"""

import os
import re
import logging
from typing import Dict, Optional, List
import requests
from datetime import datetime, timezone

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpenseCategorizer:
    """AI-powered expense categorization using Hugging Face models"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Standard expense categories for financial apps
        self.categories = [
            "Food & Dining",
            "Transportation", 
            "Entertainment",
            "Shopping",
            "Utilities",
            "Healthcare",
            "Housing",
            "Education",
            "Travel",
            "Business",
            "Other"
        ]
        
        # Hugging Face model for text classification
        self.hf_model = "facebook/bart-large-mnli"
        self.hf_api_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
        
        # Fallback rule-based patterns
        self.category_patterns = {
            'Food & Dining': [
                'coffee', 'restaurant', 'food', 'lunch', 'dinner', 'breakfast',
                'eat', 'starbucks', 'mcdonalds', 'pizza', 'burger', 'cafe',
                'dining', 'meal', 'snack', 'grocery', 'supermarket'
            ],
            'Transportation': [
                'uber', 'lyft', 'taxi', 'gas', 'fuel', 'transport', 'bus', 
                'train', 'subway', 'metro', 'parking', 'toll', 'car', 'vehicle'
            ],
            'Entertainment': [
                'netflix', 'spotify', 'movie', 'game', 'entertainment', 'cinema',
                'theater', 'music', 'streaming', 'subscription', 'youtube', 'amazon prime'
            ],
            'Utilities': [
                'electric', 'electricity', 'water', 'internet', 'phone', 'utility',
                'cable', 'wifi', 'cellular', 'mobile', 'landline'
            ],
            'Housing': [
                'rent', 'mortgage', 'insurance', 'home', 'house', 'apartment',
                'property', 'maintenance', 'repair', 'furnishing'
            ],
            'Healthcare': [
                'doctor', 'pharmacy', 'medical', 'health', 'hospital', 'clinic',
                'prescription', 'medicine', 'dental', 'vision', 'therapy'
            ],
            'Shopping': [
                'clothes', 'shopping', 'amazon', 'store', 'buy', 'purchase',
                'retail', 'mall', 'online', 'clothing', 'shoes', 'accessories'
            ],
            'Education': [
                'school', 'university', 'course', 'book', 'education', 'tuition',
                'learning', 'training', 'certification', 'seminar'
            ],
            'Travel': [
                'hotel', 'flight', 'travel', 'vacation', 'trip', 'airline',
                'booking', 'airbnb', 'resort', 'cruise', 'tour'
            ],
            'Business': [
                'office', 'business', 'meeting', 'conference', 'work', 'professional',
                'equipment', 'software', 'tools', 'supplies'
            ]
        }
    
    async def categorize_with_ai(self, description: str, amount: float = None) -> str:
        """
        Categorize expense using AI models
        """
        try:
            # Try Hugging Face first
            if self.hf_api_key:
                category = await self._categorize_with_huggingface(description)
                if category:
                    logger.info(f"✅ HuggingFace categorized '{description}' as '{category}'")
                    return category
            
            # Try Groq as fallback
            if self.groq_api_key:
                category = await self._categorize_with_groq(description, amount)
                if category:
                    logger.info(f"✅ Groq categorized '{description}' as '{category}'")
                    return category
            
            # Fallback to rule-based
            category = self._categorize_with_rules(description)
            logger.info(f"✅ Rule-based categorized '{description}' as '{category}'")
            return category
            
        except Exception as e:
            logger.error(f"❌ AI categorization failed: {e}")
            return self._categorize_with_rules(description)
    
    async def _categorize_with_huggingface(self, description: str) -> Optional[str]:
        """Use Hugging Face BART model for zero-shot classification"""
        try:
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            # Prepare the classification prompt
            payload = {
                "inputs": description,
                "parameters": {
                    "candidate_labels": self.categories
                }
            }
            
            response = requests.post(
                self.hf_api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result and 'labels' in result and result['labels']:
                    # Return the highest confidence category
                    best_category = result['labels'][0]
                    confidence = result['scores'][0]
                    
                    # Only return if confidence is above threshold
                    if confidence > 0.3:
                        return best_category
            
            return None
            
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
            return None
    
    async def _categorize_with_groq(self, description: str, amount: float = None) -> Optional[str]:
        """Use Groq for fast inference categorization"""
        try:
            # This would be implemented with Groq API
            # For now, return None to fall back to rules
            return None
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None
    
    def _categorize_with_rules(self, description: str) -> str:
        """Fallback rule-based categorization"""
        desc_lower = description.lower()
        
        # Clean the description for better matching
        desc_clean = re.sub(r'[^\w\s]', ' ', desc_lower)
        
        # Score each category
        category_scores = {}
        for category, patterns in self.category_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in desc_clean:
                    # Exact word match gets higher score
                    if f" {pattern} " in f" {desc_clean} ":
                        score += 2
                    else:
                        score += 1
            category_scores[category] = score
        
        # Return the highest scoring category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:
                return best_category[0]
        
        return 'Other'
    
    def get_category_insights(self, description: str, predicted_category: str) -> Dict:
        """Generate insights about the categorization"""
        confidence_factors = []
        desc_lower = description.lower()
        
        if predicted_category in self.category_patterns:
            matched_patterns = [
                pattern for pattern in self.category_patterns[predicted_category]
                if pattern in desc_lower
            ]
            confidence_factors = matched_patterns
        
        return {
            "predicted_category": predicted_category,
            "confidence_factors": confidence_factors,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global instance
expense_categorizer = ExpenseCategorizer()

# Convenience function for easy import
async def categorize_expense_ai(description: str, amount: float = None) -> str:
    """Main function to categorize an expense using AI"""
    return await expense_categorizer.categorize_with_ai(description, amount)

def categorize_expense_rules(description: str) -> str:
    """Fallback function for rule-based categorization"""
    return expense_categorizer._categorize_with_rules(description)
