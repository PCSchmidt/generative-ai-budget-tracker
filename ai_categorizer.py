# ai_categorizer.py - Main AI categorization module for local development
import os
from typing import Optional, Dict, Any
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import asyncio
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpenseCategorizer:
    """Main expense categorization class using Hugging Face models"""
    
    def __init__(self):
        """Initialize the categorizer with local model or API fallback"""
        self.model = None
        self.tokenizer = None
        self.classifier = None
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model_name = "facebook/bart-large-mnli"
        
        # Financial categories for classification
        self.categories = [
            "Food and Dining",
            "Transportation", 
            "Shopping",
            "Entertainment",
            "Bills and Utilities",
            "Healthcare",
            "Travel",
            "Business",
            "Education",
            "Personal Care",
            "Home and Garden",
            "Other"
        ]
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model for categorization"""
        try:
            logger.info("Initializing AI categorization model...")
            
            # Try to load local model first
            self.classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=-1  # Use CPU
            )
            logger.info("✅ Local AI model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load local model: {e}")
            logger.info("Will use API-based classification as fallback")
    
    async def categorize_expense(self, description: str, amount: float = None) -> Dict[str, Any]:
        """
        Categorize an expense description using AI
        
        Args:
            description: The expense description
            amount: Optional amount (can influence categorization)
            
        Returns:
            Dict with category, confidence, and method used
        """
        if not description or not description.strip():
            return {
                "category": "Other",
                "confidence": 0.5,
                "method": "default",
                "success": True
            }
        
        # Clean the description
        clean_description = description.strip().lower()
        
        # Try local model first
        if self.classifier:
            try:
                result = self.classifier(clean_description, self.categories)
                
                return {
                    "category": result['labels'][0],
                    "confidence": round(result['scores'][0], 3),
                    "method": "local_ai",
                    "success": True,
                    "all_scores": dict(zip(result['labels'], result['scores']))
                }
                
            except Exception as e:
                logger.warning(f"Local AI classification failed: {e}")
        
        # Fallback to API-based classification
        if self.api_key:
            try:
                return await self._api_categorize(clean_description)
            except Exception as e:
                logger.warning(f"API classification failed: {e}")
        
        # Final fallback to keyword-based classification
        return self._keyword_categorize(clean_description)
    
    async def _api_categorize(self, description: str) -> Dict[str, Any]:
        """Use Hugging Face API for categorization"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": description,
            "parameters": {
                "candidate_labels": self.categories
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{self.model_name}",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                return {
                    "category": result['labels'][0],
                    "confidence": round(result['scores'][0], 3),
                    "method": "api_ai",
                    "success": True,
                    "all_scores": dict(zip(result['labels'], result['scores']))
                }
            else:
                raise Exception(f"API request failed: {response.status_code}")
    
    def _keyword_categorize(self, description: str) -> Dict[str, Any]:
        """Fallback keyword-based categorization"""
        
        # Keyword mappings for different categories
        keyword_map = {
            "Food and Dining": [
                "restaurant", "food", "lunch", "dinner", "breakfast", "coffee", 
                "pizza", "burger", "meal", "grocery", "supermarket", "cafe",
                "starbucks", "mcdonald", "subway", "domino", "uber eats", "doordash"
            ],
            "Transportation": [
                "uber", "lyft", "taxi", "gas", "fuel", "parking", "metro", 
                "bus", "train", "flight", "airline", "car", "vehicle", "toll"
            ],
            "Shopping": [
                "amazon", "walmart", "target", "shopping", "store", "mall", 
                "clothing", "shoes", "electronics", "online", "purchase"
            ],
            "Entertainment": [
                "movie", "cinema", "netflix", "spotify", "gaming", "concert", 
                "theater", "entertainment", "music", "streaming", "youtube"
            ],
            "Bills and Utilities": [
                "electric", "electricity", "water", "gas", "internet", "phone", 
                "cable", "utility", "bill", "payment", "subscription"
            ],
            "Healthcare": [
                "doctor", "hospital", "pharmacy", "medical", "health", "dentist", 
                "insurance", "medicine", "prescription", "clinic"
            ],
            "Travel": [
                "hotel", "flight", "vacation", "travel", "trip", "booking", 
                "airbnb", "rental", "tourism", "holiday"
            ],
            "Business": [
                "office", "business", "meeting", "conference", "supplies", 
                "equipment", "software", "professional", "service"
            ]
        }
        
        # Count keyword matches for each category
        scores = {}
        words = description.lower().split()
        
        for category, keywords in keyword_map.items():
            score = 0
            for keyword in keywords:
                if keyword in description:
                    score += 1
                    # Bonus for exact word matches
                    if keyword in words:
                        score += 0.5
            scores[category] = score
        
        # Find best match
        if scores and max(scores.values()) > 0:
            best_category = max(scores, key=scores.get)
            confidence = min(0.9, max(scores.values()) / 3)  # Normalize confidence
            
            return {
                "category": best_category,
                "confidence": round(confidence, 3),
                "method": "keyword",
                "success": True,
                "keyword_scores": scores
            }
        
        # Default fallback
        return {
            "category": "Other",
            "confidence": 0.3,
            "method": "default",
            "success": True
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model setup"""
        return {
            "model_name": self.model_name,
            "local_model_loaded": self.classifier is not None,
            "api_key_available": bool(self.api_key),
            "categories": self.categories,
            "fallback_methods": ["local_ai", "api_ai", "keyword", "default"]
        }

# Global instance
categorizer = ExpenseCategorizer()

# Main functions for backward compatibility
async def categorize_expense(description: str, amount: float = None) -> Dict[str, Any]:
    """Main categorization function"""
    return await categorizer.categorize_expense(description, amount)

def get_categories() -> list:
    """Get available categories"""
    return categorizer.categories

def get_model_info() -> Dict[str, Any]:
    """Get model information"""
    return categorizer.get_model_info()
