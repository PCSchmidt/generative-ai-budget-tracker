"""
Enhanced ML-powered expense categorization service for AI Budget Tracker.
Implements multiple classification strategies with intelligent fallbacks.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedExpenseCategorizer:
    """
    Advanced expense categorization using multiple ML strategies:
    1. Local ML models (Hugging Face transformers)
    2. API-based classification fallback
    3. Pattern learning from user behavior
    4. Semantic similarity matching
    5. Enhanced rule-based classification
    """
    
    def __init__(self):
        """Initialize the enhanced categorizer with all classification strategies."""
        self.local_model = None
        self.vectorizer = None
        self.category_cache = {}
        self.user_patterns = {}
        self.classification_stats = {
            "total_classifications": 0,
            "ml_model_used": 0,
            "rule_based_used": 0,
            "pattern_based_used": 0,
            "cache_hits": 0
        }
        
        # Initialize all strategies
        self._initialize_local_model()
        self._initialize_category_definitions()
        self._initialize_pattern_learning()
        self._initialize_semantic_matching()
        
    def _initialize_local_model(self):
        """Initialize local Hugging Face model for classification."""
        try:
            from transformers import pipeline
            
            # Use a pre-trained text classification model
            # This is a lightweight model that works well for categorization
            self.local_model = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",
                device=-1  # Use CPU
            )
            logger.info("✅ Local ML model initialized successfully")
            
        except ImportError:
            logger.warning("⚠️ Transformers not available, using fallback strategies")
            self.local_model = None
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize local model: {e}")
            self.local_model = None
    
    def _initialize_category_definitions(self):
        """Initialize comprehensive category definitions and keywords."""
        self.categories = {
            "Food & Dining": {
                "keywords": [
                    "restaurant", "food", "dining", "cafe", "coffee", "starbucks", "mcdonalds",
                    "burger", "pizza", "sushi", "thai", "chinese", "mexican", "italian",
                    "breakfast", "lunch", "dinner", "snack", "bakery", "deli", "bistro",
                    "grill", "bar", "pub", "brewery", "wine", "alcohol", "grocery", "supermarket",
                    "whole foods", "trader joes", "safeway", "kroger", "target", "walmart",
                    "costco", "market", "fresh", "organic", "produce"
                ],
                "patterns": [
                    r".*restaurant.*", r".*food.*", r".*dining.*", r".*cafe.*",
                    r".*grocery.*", r".*market.*", r".*fresh.*"
                ],
                "amount_ranges": [(0, 500)]  # Typical food expense range
            },
            
            "Transportation": {
                "keywords": [
                    "uber", "lyft", "taxi", "gas", "fuel", "shell", "exxon", "chevron",
                    "bp", "mobil", "station", "parking", "garage", "meter", "toll",
                    "subway", "metro", "bus", "train", "airline", "flight", "airport",
                    "car", "auto", "vehicle", "maintenance", "repair", "oil", "tire",
                    "insurance", "registration", "dmv"
                ],
                "patterns": [
                    r".*gas.*station.*", r".*uber.*", r".*lyft.*", r".*taxi.*",
                    r".*parking.*", r".*toll.*", r".*airline.*", r".*flight.*"
                ],
                "amount_ranges": [(5, 200), (200, 2000)]  # Rides vs flights/repairs
            },
            
            "Entertainment": {
                "keywords": [
                    "netflix", "spotify", "hulu", "disney", "amazon prime", "youtube",
                    "movie", "cinema", "theater", "concert", "show", "ticket", "event",
                    "game", "gaming", "steam", "playstation", "xbox", "nintendo",
                    "book", "kindle", "audible", "magazine", "subscription", "streaming",
                    "music", "podcast", "app store", "google play"
                ],
                "patterns": [
                    r".*netflix.*", r".*spotify.*", r".*streaming.*", r".*subscription.*",
                    r".*movie.*", r".*concert.*", r".*game.*", r".*entertainment.*"
                ],
                "amount_ranges": [(0.99, 100)]  # Typical entertainment costs
            },
            
            "Utilities & Bills": {
                "keywords": [
                    "electric", "electricity", "power", "energy", "utility", "gas",
                    "water", "sewer", "internet", "wifi", "phone", "mobile", "cellular",
                    "cable", "tv", "television", "verizon", "att", "tmobile", "sprint",
                    "comcast", "spectrum", "bill", "payment", "service", "account"
                ],
                "patterns": [
                    r".*electric.*", r".*utility.*", r".*bill.*", r".*payment.*",
                    r".*service.*", r".*verizon.*", r".*comcast.*", r".*spectrum.*"
                ],
                "amount_ranges": [(20, 300)]  # Typical utility bills
            },
            
            "Shopping": {
                "keywords": [
                    "amazon", "ebay", "store", "shop", "retail", "purchase", "buy",
                    "clothing", "clothes", "fashion", "shoes", "accessories", "jewelry",
                    "electronics", "computer", "phone", "laptop", "tablet", "gadget",
                    "home", "furniture", "decor", "appliance", "tool", "hardware",
                    "best buy", "target", "walmart", "costco", "online", "delivery"
                ],
                "patterns": [
                    r".*amazon.*", r".*store.*", r".*shop.*", r".*retail.*",
                    r".*clothing.*", r".*electronics.*", r".*purchase.*"
                ],
                "amount_ranges": [(5, 1000)]  # Wide range for shopping
            },
            
            "Health & Fitness": {
                "keywords": [
                    "gym", "fitness", "workout", "health", "medical", "doctor", "hospital",
                    "pharmacy", "medicine", "prescription", "dental", "dentist", "vision",
                    "optometry", "therapy", "massage", "spa", "wellness", "supplement",
                    "vitamin", "protein", "nutrition", "personal trainer", "yoga",
                    "pilates", "crossfit", "membership"
                ],
                "patterns": [
                    r".*gym.*", r".*fitness.*", r".*medical.*", r".*health.*",
                    r".*pharmacy.*", r".*doctor.*", r".*dental.*"
                ],
                "amount_ranges": [(10, 500)]  # Health and fitness costs
            },
            
            "Education": {
                "keywords": [
                    "school", "university", "college", "tuition", "education", "course",
                    "class", "lesson", "training", "certification", "book", "textbook",
                    "supplies", "student", "academic", "learning", "online course",
                    "udemy", "coursera", "edx", "skillshare", "masterclass"
                ],
                "patterns": [
                    r".*school.*", r".*university.*", r".*course.*", r".*education.*",
                    r".*tuition.*", r".*training.*", r".*certification.*"
                ],
                "amount_ranges": [(20, 5000)]  # Education costs vary widely
            },
            
            "Travel": {
                "keywords": [
                    "hotel", "motel", "airbnb", "booking", "travel", "vacation", "trip",
                    "flight", "airline", "airport", "rental car", "car rental", "cruise",
                    "resort", "tour", "ticket", "visa", "passport", "luggage", "travel insurance"
                ],
                "patterns": [
                    r".*hotel.*", r".*travel.*", r".*flight.*", r".*vacation.*",
                    r".*airbnb.*", r".*booking.*", r".*rental.*"
                ],
                "amount_ranges": [(50, 3000)]  # Travel costs vary widely
            },
            
            "Miscellaneous": {
                "keywords": [
                    "misc", "other", "various", "general", "unknown", "cash", "atm",
                    "fee", "charge", "service", "payment", "transfer", "deposit"
                ],
                "patterns": [
                    r".*misc.*", r".*other.*", r".*unknown.*", r".*fee.*",
                    r".*charge.*", r".*atm.*"
                ],
                "amount_ranges": [(0, 10000)]  # Catch-all category
            }
        }
    
    def _initialize_pattern_learning(self):
        """Initialize pattern learning from user behavior."""
        self.user_patterns = {
            "merchant_categories": {},  # merchant -> category mapping
            "amount_patterns": {},      # amount range -> likely category
            "time_patterns": {},        # time-based categorization patterns
            "description_patterns": {}  # learned description patterns
        }
    
    def _initialize_semantic_matching(self):
        """Initialize semantic similarity matching."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=1000
            )
            
            # Create category descriptions for similarity matching
            self.category_descriptions = {}
            for category, data in self.categories.items():
                # Combine keywords into a description
                description = " ".join(data["keywords"][:20])  # Use top keywords
                self.category_descriptions[category] = description
            
            # Fit vectorizer on category descriptions
            category_texts = list(self.category_descriptions.values())
            self.category_vectors = self.vectorizer.fit_transform(category_texts)
            
            logger.info("✅ Semantic matching initialized")
            
        except ImportError:
            logger.warning("⚠️ Scikit-learn not available for semantic matching")
            self.vectorizer = None
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize semantic matching: {e}")
            self.vectorizer = None
    
    def categorize(self, description: str, amount: float, user_id: Optional[str] = None) -> str:
        """
        Categorize an expense using multiple ML strategies.
        
        Args:
            description: Expense description text
            amount: Expense amount
            user_id: Optional user ID for personalized learning
            
        Returns:
            Category name as string
        """
        self.classification_stats["total_classifications"] += 1
        
        # Normalize inputs
        description = description.lower().strip()
        cache_key = f"{description}_{amount}"
        
        # Strategy 1: Check cache first
        if cache_key in self.category_cache:
            self.classification_stats["cache_hits"] += 1
            return self.category_cache[cache_key]
        
        # Strategy 2: Try local ML model
        ml_category = self._classify_with_local_model(description, amount)
        if ml_category:
            self.classification_stats["ml_model_used"] += 1
            category = ml_category
        else:
            # Strategy 3: Pattern-based learning
            pattern_category = self._classify_with_patterns(description, amount, user_id)
            if pattern_category:
                self.classification_stats["pattern_based_used"] += 1
                category = pattern_category
            else:
                # Strategy 4: Semantic similarity
                semantic_category = self._classify_with_semantics(description, amount)
                if semantic_category:
                    category = semantic_category
                else:
                    # Strategy 5: Enhanced rule-based (fallback)
                    self.classification_stats["rule_based_used"] += 1
                    category = self._classify_with_enhanced_rules(description, amount)
        
        # Cache the result
        self.category_cache[cache_key] = category
        
        # Learn from this classification
        self._learn_from_classification(description, amount, category, user_id)
        
        return category
    
    def _classify_with_local_model(self, description: str, amount: float) -> Optional[str]:
        """Classify using local Hugging Face model."""
        if not self.local_model:
            return None
        
        try:
            # Create hypotheses for each category
            hypotheses = list(self.categories.keys())
            
            # Use MNLI model to classify
            premise = f"This expense '{description}' for ${amount:.2f} is for"
            
            best_category = None
            best_score = 0
            
            for category in hypotheses:
                # Create hypothesis
                hypothesis = f"This is a {category.lower()} expense"
                
                # Get classification result
                result = self.local_model(premise, hypothesis)
                
                # Check if it's entailed (positive classification)
                if result['label'] == 'ENTAILMENT' and result['score'] > best_score:
                    best_score = result['score']
                    best_category = category
            
            # Return category if confidence is high enough
            if best_score > 0.7:
                return best_category
                
        except Exception as e:
            logger.warning(f"Local model classification failed: {e}")
        
        return None
    
    def _classify_with_patterns(self, description: str, amount: float, user_id: Optional[str]) -> Optional[str]:
        """Classify using learned patterns."""
        if not user_id or not self.user_patterns:
            return None
        
        # Check merchant patterns
        for merchant, category in self.user_patterns.get("merchant_categories", {}).items():
            if merchant.lower() in description.lower():
                return category
        
        # Check description patterns
        for pattern, category in self.user_patterns.get("description_patterns", {}).items():
            if re.search(pattern, description, re.IGNORECASE):
                return category
        
        return None
    
    def _classify_with_semantics(self, description: str, amount: float) -> Optional[str]:
        """Classify using semantic similarity."""
        if not self.vectorizer:
            return None
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            # Vectorize the description
            desc_vector = self.vectorizer.transform([description])
            
            # Calculate similarities
            similarities = cosine_similarity(desc_vector, self.category_vectors)[0]
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            # Return category if similarity is high enough
            if best_score > 0.3:  # Threshold for semantic similarity
                categories = list(self.categories.keys())
                return categories[best_idx]
                
        except Exception as e:
            logger.warning(f"Semantic classification failed: {e}")
        
        return None
    
    def _classify_with_enhanced_rules(self, description: str, amount: float) -> str:
        """Enhanced rule-based classification with smart scoring."""
        category_scores = {}
        
        for category, data in self.categories.items():
            score = 0
            
            # Keyword matching with weights
            for keyword in data["keywords"]:
                if keyword in description:
                    # Longer keywords get higher scores
                    weight = len(keyword) / 10 + 1
                    score += weight
            
            # Pattern matching
            for pattern in data["patterns"]:
                if re.search(pattern, description, re.IGNORECASE):
                    score += 3  # Pattern matches get higher scores
            
            # Amount range consideration
            for min_amount, max_amount in data["amount_ranges"]:
                if min_amount <= amount <= max_amount:
                    score += 1
            
            # Merchant-specific logic
            score += self._get_merchant_score(description, category)
            
            category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:
                return best_category[0]
        
        return "Miscellaneous"  # Default fallback
    
    def _get_merchant_score(self, description: str, category: str) -> float:
        """Get additional score based on known merchant patterns."""
        merchant_mappings = {
            "Food & Dining": ["starbucks", "mcdonalds", "subway", "dominos", "pizza hut"],
            "Transportation": ["uber", "lyft", "shell", "exxon", "chevron"],
            "Entertainment": ["netflix", "spotify", "steam", "movie"],
            "Shopping": ["amazon", "ebay", "walmart", "target"],
            "Utilities & Bills": ["verizon", "comcast", "pg&e", "electric"]
        }
        
        merchants = merchant_mappings.get(category, [])
        for merchant in merchants:
            if merchant in description:
                return 2.0  # Strong merchant match
        
        return 0.0
    
    def _learn_from_classification(self, description: str, amount: float, category: str, user_id: Optional[str]):
        """Learn patterns from successful classifications."""
        if not user_id:
            return
        
        # Extract potential merchant name (first word or known pattern)
        words = description.split()
        if words:
            potential_merchant = words[0]
            if len(potential_merchant) > 3:  # Avoid learning from short words
                self.user_patterns["merchant_categories"][potential_merchant] = category
        
        # Learn description patterns
        if len(description) > 5:
            # Create a simple pattern from the description
            pattern = re.escape(description[:10])  # First 10 characters
            self.user_patterns["description_patterns"][pattern] = category
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics and performance metrics."""
        total = self.classification_stats["total_classifications"]
        if total == 0:
            return self.classification_stats
        
        stats = self.classification_stats.copy()
        stats["ml_model_percentage"] = (stats["ml_model_used"] / total) * 100
        stats["rule_based_percentage"] = (stats["rule_based_used"] / total) * 100
        stats["pattern_based_percentage"] = (stats["pattern_based_used"] / total) * 100
        stats["cache_hit_rate"] = (stats["cache_hits"] / total) * 100
        
        return stats
    
    def batch_categorize(self, expenses: List[Tuple[str, float]]) -> List[str]:
        """Efficiently categorize multiple expenses."""
        return [self.categorize(desc, amount) for desc, amount in expenses]
    
    def update_user_patterns(self, user_corrections: Dict[str, str], user_id: str):
        """Update patterns based on user corrections."""
        for description, correct_category in user_corrections.items():
            # Learn from user feedback
            words = description.lower().split()
            if words:
                merchant = words[0]
                self.user_patterns["merchant_categories"][merchant] = correct_category
    
    def export_patterns(self, user_id: str) -> Dict[str, Any]:
        """Export learned patterns for a user."""
        return {
            "user_id": user_id,
            "patterns": self.user_patterns,
            "stats": self.get_classification_stats(),
            "exported_at": datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize categorizer
    categorizer = EnhancedExpenseCategorizer()
    
    # Test expenses
    test_expenses = [
        ("Starbucks Coffee Shop", 4.95),
        ("Shell Gas Station", 45.00),
        ("Netflix Subscription", 15.99),
        ("Uber Ride", 18.50),
        ("Amazon Purchase", 67.89),
        ("Gym Membership", 49.99),
        ("Electric Bill", 125.00),
        ("Whole Foods Market", 78.45)
    ]
    
    print("🧪 Testing Enhanced ML Categorization:")
    print("-" * 50)
    
    for description, amount in test_expenses:
        category = categorizer.categorize(description, amount)
        print(f"'{description}' (${amount}) -> {category}")
    
    print("\n📊 Classification Statistics:")
    stats = categorizer.get_classification_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
