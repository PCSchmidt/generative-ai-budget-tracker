"""
AI Expense Categorization Service
Handles automatic categorization of expenses using Hugging Face models
"""

import os
import logging
from typing import Dict, List, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import httpx
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpenseCategorizer:
    """AI-powered expense categorization using Hugging Face models"""
    
    def __init__(self):
        self.categories = {
            "FOOD": ["food", "dining", "restaurant", "grocery", "coffee", "lunch", "dinner", "breakfast"],
            "TRANSPORTATION": ["gas", "fuel", "uber", "lyft", "taxi", "parking", "metro", "bus", "train"],
            "ENTERTAINMENT": ["movie", "cinema", "concert", "game", "entertainment", "streaming"],
            "SHOPPING": ["clothing", "amazon", "store", "retail", "purchase", "buy"],
            "UTILITIES": ["electric", "water", "internet", "phone", "cable", "utility"],
            "HEALTHCARE": ["doctor", "medicine", "pharmacy", "hospital", "medical"],
            "EDUCATION": ["school", "course", "book", "tuition", "education"],
            "OTHER": []
        }
        
        # Try to initialize Hugging Face model (fallback to keyword matching)
        self.classifier = None
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model for categorization"""
        try:
            if self.hf_api_key:
                # Use Hugging Face Inference API for lightweight deployment
                logger.info("Using Hugging Face Inference API for categorization")
                self.use_api = True
            else:
                logger.warning("No Hugging Face API key found, using keyword matching")
                self.use_api = False
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {e}")
            self.use_api = False
    
    async def categorize_expense(self, description: str, amount: float = None) -> Dict:
        """
        Categorize an expense based on description and amount
        Returns category with confidence score
        """
        description = description.lower().strip()
        
        if self.use_api and self.hf_api_key:
            # Try AI categorization first
            ai_result = await self._categorize_with_ai(description)
            if ai_result:
                return ai_result
        
        # Fallback to keyword matching
        return self._categorize_with_keywords(description, amount)
    
    async def _categorize_with_ai(self, description: str) -> Optional[Dict]:
        """Use Hugging Face API for intelligent categorization"""
        try:
            # Use a general classification model that can work for expense categorization
            api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            # Create classification prompt
            candidate_labels = list(self.categories.keys())
            payload = {
                "inputs": description,
                "parameters": {"candidate_labels": candidate_labels}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, headers=headers, json=payload, timeout=10.0)
                
                if response.status_code == 200:
                    result = response.json()
                    if "labels" in result and result["labels"]:
                        category = result["labels"][0]
                        confidence = result["scores"][0] if "scores" in result else 0.8
                        
                        return {
                            "category": category,
                            "confidence": round(confidence, 2),
                            "method": "ai_classification",
                            "all_predictions": [
                                {"category": label, "confidence": round(score, 2)}
                                for label, score in zip(result.get("labels", []), result.get("scores", []))
                            ][:3]  # Top 3 predictions
                        }
                        
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
            return None
    
    def _categorize_with_keywords(self, description: str, amount: float = None) -> Dict:
        """Fallback keyword-based categorization"""
        description = description.lower()
        
        # Check for keywords in each category
        for category, keywords in self.categories.items():
            if category == "OTHER":
                continue
                
            for keyword in keywords:
                if keyword in description:
                    confidence = 0.7  # Medium confidence for keyword matching
                    
                    # Adjust confidence based on amount for certain categories
                    if amount:
                        if category == "FOOD" and amount < 50:
                            confidence = 0.8
                        elif category == "TRANSPORTATION" and 20 <= amount <= 100:
                            confidence = 0.8
                        elif category == "UTILITIES" and amount > 50:
                            confidence = 0.8
                    
                    return {
                        "category": category,
                        "confidence": confidence,
                        "method": "keyword_matching",
                        "matched_keyword": keyword,
                        "all_predictions": [
                            {"category": category, "confidence": confidence}
                        ]
                    }
        
        # Default to OTHER if no match found
        return {
            "category": "OTHER",
            "confidence": 0.3,
            "method": "default",
            "all_predictions": [
                {"category": "OTHER", "confidence": 0.3}
            ]
        }
    
    def get_category_suggestions(self, description: str) -> List[str]:
        """Get suggested categories for manual override"""
        # Return categories sorted by likelihood
        return list(self.categories.keys())

# Global instance
expense_categorizer = ExpenseCategorizer()
