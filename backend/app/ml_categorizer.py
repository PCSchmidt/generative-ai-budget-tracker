"""
Enhanced ML Expense Categorization Service
Combines Hugging Face transformers with advanced ML techniques
"""

import os
import json
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import asyncio
import numpy as np
from collections import defaultdict, Counter

# ML imports with fallback handling
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logging.warning("Transformers not available, using API-only mode")

try:
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available, using basic classification")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedExpenseCategorizer:
    """
    Advanced ML-powered expense categorization with multiple strategies:
    1. Local Hugging Face transformer models
    2. API-based classification with confidence scoring
    3. Historical pattern learning
    4. Semantic similarity matching
    5. Rule-based fallback
    """
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Enhanced category system with subcategories
        self.categories = {
            "Food & Dining": ["restaurants", "fast_food", "groceries", "coffee", "delivery"],
            "Transportation": ["gas", "public_transport", "rideshare", "parking", "maintenance"],
            "Entertainment": ["streaming", "movies", "games", "events", "hobbies"],
            "Shopping": ["clothing", "electronics", "home_goods", "online", "retail"],
            "Utilities": ["electricity", "water", "internet", "phone", "cable"],
            "Healthcare": ["medical", "pharmacy", "insurance", "fitness", "wellness"],
            "Housing": ["rent", "mortgage", "maintenance", "furniture", "insurance"],
            "Education": ["tuition", "books", "courses", "training", "certifications"],
            "Travel": ["flights", "hotels", "vacation", "business_travel", "local_trips"],
            "Business": ["office_supplies", "software", "equipment", "meetings", "services"],
            "Other": ["miscellaneous", "personal", "gifts", "donations", "fees"]
        }
        
        # Flatten categories for classification
        self.category_list = list(self.categories.keys())
        
        # Initialize ML models
        self.local_model = None
        self.tokenizer = None
        self.vectorizer = None
        
        # User learning data
        self.user_patterns = defaultdict(list)
        self.category_history = defaultdict(int)
        
        # Performance tracking
        self.classification_stats = {
            "total_classifications": 0,
            "ml_success": 0,
            "api_success": 0,
            "rule_fallback": 0,
            "confidence_scores": []
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize local ML models if available"""
        try:
            if HF_AVAILABLE:
                logger.info("🚀 Initializing local Hugging Face models...")
                # Use a lightweight, fast model for local inference
                model_name = "microsoft/DialoGPT-medium"  # Fast and efficient
                
                # Initialize with error handling
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
                    logger.info("✅ Tokenizer loaded successfully")
                    
                    # Initialize zero-shot classification pipeline
                    self.classifier = pipeline(
                        "zero-shot-classification",
                        model="facebook/bart-large-mnli",
                        device=-1  # Use CPU for reliability
                    )
                    logger.info("✅ Local ML model initialized successfully")
                    
                except Exception as e:
                    logger.warning(f"Local model initialization failed: {e}")
                    self.classifier = None
            
            if SKLEARN_AVAILABLE:
                # Initialize TF-IDF vectorizer for semantic similarity
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                logger.info("✅ TF-IDF vectorizer initialized")
                
        except Exception as e:
            logger.error(f"❌ Model initialization error: {e}")
    
    async def categorize_expense(self, description: str, amount: float = None, user_id: str = None) -> Dict:
        """
        Enhanced categorization with multiple ML strategies
        Returns detailed classification results with confidence scores
        """
        start_time = datetime.now()
        
        # Clean and preprocess description
        clean_description = self._preprocess_description(description)
        
        result = {
            "description": description,
            "clean_description": clean_description,
            "amount": amount,
            "category": "Other",
            "subcategory": None,
            "confidence": 0.0,
            "method": "fallback",
            "processing_time_ms": 0,
            "alternatives": [],
            "reasoning": ""
        }
        
        try:
            # Strategy 1: Local ML model (fastest and most reliable)
            if self.classifier:
                ml_result = await self._classify_with_local_model(clean_description)
                if ml_result and ml_result["confidence"] > 0.6:
                    result.update(ml_result)
                    result["method"] = "local_ml"
                    self.classification_stats["ml_success"] += 1
                    logger.info(f"✅ Local ML: '{description}' → '{result['category']}' ({result['confidence']:.2f})")
            
            # Strategy 2: API-based classification (if local fails)
            if result["confidence"] < 0.6 and self.hf_api_key:
                api_result = await self._classify_with_api(clean_description)
                if api_result and api_result["confidence"] > result["confidence"]:
                    result.update(api_result)
                    result["method"] = "api_ml"
                    self.classification_stats["api_success"] += 1
                    logger.info(f"✅ API ML: '{description}' → '{result['category']}' ({result['confidence']:.2f})")
            
            # Strategy 3: Historical pattern matching
            if result["confidence"] < 0.5 and user_id:
                pattern_result = self._classify_with_patterns(clean_description, user_id)
                if pattern_result and pattern_result["confidence"] > result["confidence"]:
                    result.update(pattern_result)
                    result["method"] = "pattern_learning"
                    logger.info(f"✅ Pattern: '{description}' → '{result['category']}' ({result['confidence']:.2f})")
            
            # Strategy 4: Semantic similarity (if sklearn available)
            if result["confidence"] < 0.4 and SKLEARN_AVAILABLE:
                similarity_result = self._classify_with_similarity(clean_description)
                if similarity_result and similarity_result["confidence"] > result["confidence"]:
                    result.update(similarity_result)
                    result["method"] = "semantic_similarity"
                    logger.info(f"✅ Similarity: '{description}' → '{result['category']}' ({result['confidence']:.2f})")
            
            # Strategy 5: Enhanced rule-based fallback
            if result["confidence"] < 0.3:
                rule_result = self._classify_with_enhanced_rules(clean_description, amount)
                result.update(rule_result)
                result["method"] = "enhanced_rules"
                self.classification_stats["rule_fallback"] += 1
                logger.info(f"✅ Rules: '{description}' → '{result['category']}' ({result['confidence']:.2f})")
            
            # Learn from this classification for future improvements
            if user_id and result["confidence"] > 0.5:
                self._learn_from_classification(clean_description, result["category"], user_id)
            
        except Exception as e:
            logger.error(f"❌ Enhanced categorization error: {e}")
            result = self._classify_with_enhanced_rules(clean_description, amount)
            result["method"] = "error_fallback"
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        result["processing_time_ms"] = round(processing_time, 2)
        
        # Update statistics
        self.classification_stats["total_classifications"] += 1
        self.classification_stats["confidence_scores"].append(result["confidence"])
        
        return result
    
    async def _classify_with_local_model(self, description: str) -> Optional[Dict]:
        """Use local Hugging Face model for classification"""
        try:
            if not self.classifier:
                return None
            
            # Run classification
            result = self.classifier(description, self.category_list)
            
            if result and 'labels' in result and 'scores' in result:
                return {
                    "category": result['labels'][0],
                    "confidence": float(result['scores'][0]),
                    "alternatives": [
                        {"category": label, "confidence": float(score)}
                        for label, score in zip(result['labels'][1:3], result['scores'][1:3])
                    ],
                    "reasoning": f"Local ML model classified based on text similarity to '{result['labels'][0]}'"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Local model classification error: {e}")
            return None
    
    async def _classify_with_api(self, description: str) -> Optional[Dict]:
        """Enhanced API classification with retry logic"""
        # Import here to avoid dependency issues
        import requests
        
        try:
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            payload = {
                "inputs": description,
                "parameters": {
                    "candidate_labels": self.category_list,
                    "multi_label": False
                }
            }
            
            api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
            
            # Retry logic for API calls
            for attempt in range(3):
                try:
                    response = requests.post(
                        api_url,
                        headers=headers,
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result and 'labels' in result and 'scores' in result:
                            return {
                                "category": result['labels'][0],
                                "confidence": float(result['scores'][0]),
                                "alternatives": [
                                    {"category": label, "confidence": float(score)}
                                    for label, score in zip(result['labels'][1:3], result['scores'][1:3])
                                ],
                                "reasoning": f"API ML model with {result['scores'][0]:.1%} confidence"
                            }
                    
                    elif response.status_code == 503:
                        # Model loading, wait and retry
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    break
                    
                except requests.RequestException as e:
                    logger.warning(f"API attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        await asyncio.sleep(1)
            
            return None
            
        except Exception as e:
            logger.error(f"API classification error: {e}")
            return None
    
    def _classify_with_patterns(self, description: str, user_id: str) -> Optional[Dict]:
        """Learn from user's historical categorization patterns"""
        try:
            user_history = self.user_patterns.get(user_id, [])
            if not user_history:
                return None
            
            # Find similar descriptions in user's history
            similarities = []
            for hist_desc, hist_category in user_history:
                similarity = self._calculate_text_similarity(description, hist_desc)
                if similarity > 0.7:  # High similarity threshold
                    similarities.append((hist_category, similarity))
            
            if similarities:
                # Get most frequent category among similar descriptions
                category_scores = defaultdict(float)
                for category, similarity in similarities:
                    category_scores[category] += similarity
                
                best_category = max(category_scores.items(), key=lambda x: x[1])
                confidence = min(best_category[1], 0.9)  # Cap at 90%
                
                return {
                    "category": best_category[0],
                    "confidence": confidence,
                    "alternatives": [],
                    "reasoning": f"Based on {len(similarities)} similar past expenses"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Pattern classification error: {e}")
            return None
    
    def _classify_with_similarity(self, description: str) -> Optional[Dict]:
        """Use TF-IDF and cosine similarity for classification"""
        try:
            if not self.vectorizer:
                return None
            
            # Create a corpus of category examples
            category_examples = []
            category_labels = []
            
            for category, subcategories in self.categories.items():
                # Add category name and subcategories as examples
                examples = [category.lower()] + subcategories
                for example in examples:
                    category_examples.append(example)
                    category_labels.append(category)
            
            # Fit vectorizer and transform
            all_texts = category_examples + [description.lower()]
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity between description and category examples
            desc_vector = tfidf_matrix[-1]
            category_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(desc_vector, category_vectors).flatten()
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]
            best_category = category_labels[best_idx]
            
            if best_similarity > 0.3:  # Minimum similarity threshold
                return {
                    "category": best_category,
                    "confidence": min(best_similarity * 1.2, 0.8),  # Boost but cap
                    "alternatives": [],
                    "reasoning": f"Semantic similarity to '{category_examples[best_idx]}'"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Similarity classification error: {e}")
            return None
    
    def _classify_with_enhanced_rules(self, description: str, amount: float = None) -> Dict:
        """Enhanced rule-based classification with amount consideration"""
        
        # Enhanced keyword patterns with weights
        enhanced_patterns = {
            'Food & Dining': {
                'high': ['restaurant', 'dining', 'food', 'meal'],
                'medium': ['coffee', 'lunch', 'dinner', 'breakfast', 'eat'],
                'low': ['starbucks', 'mcdonald', 'pizza', 'burger', 'cafe', 'grocery']
            },
            'Transportation': {
                'high': ['uber', 'lyft', 'taxi', 'gas', 'fuel'],
                'medium': ['transport', 'bus', 'train', 'subway', 'parking'],
                'low': ['toll', 'car', 'vehicle', 'metro']
            },
            'Entertainment': {
                'high': ['netflix', 'spotify', 'movie', 'entertainment'],
                'medium': ['cinema', 'theater', 'music', 'streaming'],
                'low': ['game', 'youtube', 'subscription']
            },
            'Shopping': {
                'high': ['amazon', 'shopping', 'store', 'purchase'],
                'medium': ['clothes', 'retail', 'mall', 'online'],
                'low': ['buy', 'clothing', 'shoes']
            },
            'Utilities': {
                'high': ['electric', 'water', 'internet', 'phone'],
                'medium': ['utility', 'cable', 'wifi', 'cellular'],
                'low': ['mobile', 'landline']
            }
        }
        
        desc_lower = description.lower()
        category_scores = defaultdict(float)
        
        # Score categories based on keyword matches
        for category, patterns in enhanced_patterns.items():
            for weight_level, keywords in patterns.items():
                weight = {'high': 3.0, 'medium': 2.0, 'low': 1.0}[weight_level]
                for keyword in keywords:
                    if keyword in desc_lower:
                        category_scores[category] += weight
        
        # Amount-based adjustments
        if amount:
            if amount > 500:  # Large amounts
                category_scores['Housing'] += 1.0
                category_scores['Travel'] += 0.5
            elif amount < 10:  # Small amounts
                category_scores['Food & Dining'] += 0.5
                category_scores['Transportation'] += 0.5
        
        # Find best category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            confidence = min(best_category[1] / 5.0, 0.7)  # Normalize and cap
            
            return {
                "category": best_category[0],
                "confidence": confidence,
                "alternatives": [
                    {"category": cat, "confidence": score / 5.0}
                    for cat, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
                ],
                "reasoning": f"Rule-based match with score {best_category[1]:.1f}"
            }
        
        # Default fallback
        return {
            "category": "Other",
            "confidence": 0.1,
            "alternatives": [],
            "reasoning": "No patterns matched, defaulted to Other"
        }
    
    def _preprocess_description(self, description: str) -> str:
        """Clean and normalize description text"""
        import re
        
        # Remove common noise
        clean = re.sub(r'[^\w\s]', ' ', description)
        clean = re.sub(r'\d+', '', clean)  # Remove numbers
        clean = re.sub(r'\s+', ' ', clean)  # Normalize whitespace
        clean = clean.strip().lower()
        
        return clean
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _learn_from_classification(self, description: str, category: str, user_id: str):
        """Store user patterns for future learning"""
        self.user_patterns[user_id].append((description, category))
        self.category_history[category] += 1
        
        # Keep only recent patterns (last 100 per user)
        if len(self.user_patterns[user_id]) > 100:
            self.user_patterns[user_id] = self.user_patterns[user_id][-100:]
    
    def get_classification_stats(self) -> Dict:
        """Get performance statistics"""
        stats = self.classification_stats.copy()
        if stats["confidence_scores"]:
            stats["average_confidence"] = np.mean(stats["confidence_scores"])
            stats["confidence_std"] = np.std(stats["confidence_scores"])
        else:
            stats["average_confidence"] = 0.0
            stats["confidence_std"] = 0.0
        
        return stats
    
    async def batch_categorize(self, expenses: List[Dict]) -> List[Dict]:
        """Efficiently categorize multiple expenses"""
        results = []
        
        for expense in expenses:
            result = await self.categorize_expense(
                expense.get("description", ""),
                expense.get("amount"),
                expense.get("user_id")
            )
            results.append(result)
        
        return results

# Global instance
enhanced_categorizer = EnhancedExpenseCategorizer()

# Convenience function for backward compatibility
async def categorize_expense(description: str, amount: float = None, user_id: str = None) -> str:
    """Simple interface that returns just the category name"""
    result = await enhanced_categorizer.categorize_expense(description, amount, user_id)
    return result["category"]

# Enhanced interface for detailed results
async def categorize_expense_detailed(description: str, amount: float = None, user_id: str = None) -> Dict:
    """Enhanced interface that returns full classification details"""
    return await enhanced_categorizer.categorize_expense(description, amount, user_id)
