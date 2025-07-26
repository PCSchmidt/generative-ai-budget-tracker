"""
Lightweight AI Categorizer for Railway Deployment
Uses Hugging Face Inference API instead of local models to reduce image size
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
import httpx
from datetime import datetime

class LightweightAICategorizer:
    """Lightweight expense categorizer using Hugging Face Inference API"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Hugging Face Inference API endpoint
        self.hf_api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        
        # Predefined categories for classification
        self.categories = [
            "Food & Dining",
            "Groceries", 
            "Transportation",
            "Gas & Fuel",
            "Entertainment",
            "Shopping",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Business Services",
            "Personal Care",
            "Home & Garden",
            "Gifts & Donations",
            "Other"
        ]
        
        # Keyword fallback mapping
        self.keyword_mapping = {
            "restaurant": "Food & Dining",
            "coffee": "Food & Dining", 
            "starbucks": "Food & Dining",
            "mcdonalds": "Food & Dining",
            "uber eats": "Food & Dining",
            "doordash": "Food & Dining",
            "grocery": "Groceries",
            "safeway": "Groceries",
            "walmart": "Groceries",
            "target": "Groceries",
            "costco": "Groceries",
            "gas": "Gas & Fuel",
            "shell": "Gas & Fuel",
            "chevron": "Gas & Fuel",
            "uber": "Transportation",
            "lyft": "Transportation",
            "metro": "Transportation",
            "netflix": "Entertainment",
            "spotify": "Entertainment",
            "amazon": "Shopping",
            "apple": "Shopping",
            "electric": "Bills & Utilities",
            "water": "Bills & Utilities",
            "internet": "Bills & Utilities",
            "phone": "Bills & Utilities"
        }
    
    async def categorize_expense(self, description: str, amount: float = None) -> Dict:
        """
        Categorize an expense using AI or keyword fallback
        
        Args:
            description: Expense description
            amount: Optional expense amount
            
        Returns:
            Dict with category, confidence, method, and alternatives
        """
        try:
            # First try Hugging Face API
            if self.hf_api_key:
                result = await self._categorize_with_huggingface(description)
                if result:
                    return result
            
            # Fallback to Groq if available
            if self.groq_api_key:
                result = await self._categorize_with_groq(description)
                if result:
                    return result
            
            # Final fallback to keyword matching
            return self._categorize_with_keywords(description)
            
        except Exception as e:
            print(f"AI categorization error: {e}")
            return self._categorize_with_keywords(description)
    
    async def _categorize_with_huggingface(self, description: str) -> Optional[Dict]:
        """Use Hugging Face Inference API for categorization"""
        try:
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            # Prepare the classification task
            candidate_labels = self.categories
            payload = {
                "inputs": f"I spent money on: {description}",
                "parameters": {"candidate_labels": candidate_labels}
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.hf_api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract the top prediction
                    top_label = result["labels"][0]
                    top_score = result["scores"][0]
                    
                    # Get alternatives
                    alternatives = [
                        {"category": label, "confidence": score}
                        for label, score in zip(result["labels"][:3], result["scores"][:3])
                    ]
                    
                    return {
                        "category": top_label,
                        "confidence": float(top_score),
                        "method": "huggingface_api",
                        "all_predictions": alternatives,
                        "timestamp": datetime.now().isoformat(),
                        "model_used": "facebook/bart-large-mnli"
                    }
                    
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            return None
    
    async def _categorize_with_groq(self, description: str) -> Optional[Dict]:
        """Use Groq API for fast categorization"""
        try:
            from groq import Groq
            
            client = Groq(api_key=self.groq_api_key)
            
            # Create a prompt for categorization
            categories_list = ", ".join(self.categories)
            prompt = f"""
            Categorize this expense: "{description}"
            
            Available categories: {categories_list}
            
            Respond with JSON only:
            {{
                "category": "selected_category",
                "confidence": 0.95,
                "reasoning": "brief explanation"
            }}
            """
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.1,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                return {
                    "category": result.get("category", "Other"),
                    "confidence": float(result.get("confidence", 0.8)),
                    "method": "groq_api",
                    "all_predictions": [{"category": result.get("category", "Other"), "confidence": result.get("confidence", 0.8)}],
                    "timestamp": datetime.now().isoformat(),
                    "reasoning": result.get("reasoning", "AI categorization")
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, extract category from text
                for category in self.categories:
                    if category.lower() in result_text.lower():
                        return {
                            "category": category,
                            "confidence": 0.7,
                            "method": "groq_api_text",
                            "all_predictions": [{"category": category, "confidence": 0.7}],
                            "timestamp": datetime.now().isoformat()
                        }
                        
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
    
    def _categorize_with_keywords(self, description: str) -> Dict:
        """Keyword-based categorization fallback"""
        description_lower = description.lower()
        
        # Check for keyword matches
        for keyword, category in self.keyword_mapping.items():
            if keyword in description_lower:
                return {
                    "category": category,
                    "confidence": 0.8,
                    "method": "keyword_match",
                    "all_predictions": [{"category": category, "confidence": 0.8}],
                    "matched_keyword": keyword,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Default to "Other" if no matches
        return {
            "category": "Other",
            "confidence": 0.3,
            "method": "default_fallback",
            "all_predictions": [{"category": "Other", "confidence": 0.3}],
            "timestamp": datetime.now().isoformat()
        }
    
    async def analyze_batch(self, expenses: List[Dict]) -> Dict:
        """Analyze multiple expenses for patterns"""
        results = []
        
        for expense in expenses:
            result = await self.categorize_expense(
                expense.get("description", ""),
                expense.get("amount", 0)
            )
            results.append({**expense, **result})
        
        # Calculate summary statistics
        total_amount = sum(exp.get("amount", 0) for exp in expenses)
        categories = {}
        methods = {}
        total_confidence = 0
        
        for result in results:
            category = result.get("category", "Other")
            method = result.get("method", "unknown")
            amount = result.get("amount", 0)
            confidence = result.get("confidence", 0)
            
            # Category totals
            if category not in categories:
                categories[category] = {"amount": 0, "count": 0}
            categories[category]["amount"] += amount
            categories[category]["count"] += 1
            
            # Method tracking
            if method not in methods:
                methods[method] = 0
            methods[method] += 1
            
            total_confidence += confidence
        
        avg_confidence = total_confidence / len(results) if results else 0
        
        return {
            "total_expenses": len(expenses),
            "total_amount": total_amount,
            "categories": categories,
            "methods": methods,
            "average_confidence": avg_confidence,
            "detailed_results": results
        }

# Global instance
lightweight_categorizer = LightweightAICategorizer()

# For backward compatibility
expense_categorizer = lightweight_categorizer
