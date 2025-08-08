"""
Enhanced Financial Advisor using Groq API
Provides real-time personalized financial advice and insights
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

# Groq import with fallback
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logging.warning("Groq not available, using mock responses")

logger = logging.getLogger(__name__)

class EnhancedFinancialAdvisor:
    """
    AI-powered financial advisor using Groq's fast LLM inference
    Provides personalized advice, spending insights, and budget optimization
    """
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        
        if GROQ_AVAILABLE and self.groq_api_key:
            try:
                self.client = Groq(api_key=self.groq_api_key)
                logger.info("✅ Groq client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Groq initialization failed: {e}")
        
        # Cache for advice to avoid repeated API calls
        self.advice_cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # Performance tracking
        self.advice_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "api_calls": 0,
            "average_response_time": 0,
            "response_times": []
        }
    
    async def generate_financial_advice(
        self, 
        user_expenses: List[Dict], 
        user_profile: Dict = None,
        advice_type: str = "general"
    ) -> Dict:
        """
        Generate personalized financial advice based on spending data
        
        Args:
            user_expenses: List of expense dictionaries
            user_profile: User financial profile (income, goals, etc.)
            advice_type: Type of advice (general, budget, savings, debt)
        """
        start_time = datetime.now()
        
        # Create cache key
        cache_key = self._create_cache_key(user_expenses, user_profile, advice_type)
        
        # Check cache first
        if cache_key in self.advice_cache:
            cache_data = self.advice_cache[cache_key]
            if datetime.now() - cache_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                self.advice_stats["cache_hits"] += 1
                logger.info("✅ Returning cached financial advice")
                return cache_data["advice"]
        
        try:
            # Analyze spending data
            spending_analysis = self._analyze_spending_patterns(user_expenses)
            
            # Generate advice using Groq
            if self.client:
                advice = await self._generate_groq_advice(
                    spending_analysis, user_profile, advice_type
                )
            else:
                advice = self._generate_fallback_advice(
                    spending_analysis, user_profile, advice_type
                )
            
            # Cache the result
            self.advice_cache[cache_key] = {
                "advice": advice,
                "timestamp": datetime.now()
            }
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.advice_stats["total_requests"] += 1
            self.advice_stats["response_times"].append(processing_time)
            
            if len(self.advice_stats["response_times"]) > 100:
                self.advice_stats["response_times"] = self.advice_stats["response_times"][-100:]
            
            self.advice_stats["average_response_time"] = sum(self.advice_stats["response_times"]) / len(self.advice_stats["response_times"])
            
            logger.info(f"✅ Generated financial advice in {processing_time:.2f}s")
            return advice
            
        except Exception as e:
            logger.error(f"❌ Financial advice generation failed: {e}")
            return self._generate_error_fallback_advice()
    
    async def _generate_groq_advice(
        self, 
        spending_analysis: Dict, 
        user_profile: Dict, 
        advice_type: str
    ) -> Dict:
        """Generate advice using Groq's fast LLM"""
        
        # Prepare context for the AI
        context = self._prepare_advice_context(spending_analysis, user_profile, advice_type)
        
        # Create the prompt based on advice type
        prompt = self._create_advice_prompt(context, advice_type)
        
        try:
            self.advice_stats["api_calls"] += 1
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",  # Fast model for real-time advice
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional financial advisor with expertise in personal finance, budgeting, and spending optimization. Provide practical, actionable advice that helps users improve their financial health."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7,
                top_p=0.9
            )
            
            advice_text = response.choices[0].message.content
            
            # Parse and structure the advice
            return self._structure_advice_response(advice_text, spending_analysis, advice_type)
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return self._generate_fallback_advice(spending_analysis, user_profile, advice_type)
    
    def _analyze_spending_patterns(self, expenses: List[Dict]) -> Dict:
        """Analyze spending patterns and extract insights"""
        
        if not expenses:
            return {"total": 0, "categories": {}, "trends": {}, "insights": []}
        
        # Basic spending analysis
        total_spending = sum(exp.get("amount", 0) for exp in expenses)
        
        # Category breakdown
        category_spending = {}
        for expense in expenses:
            category = expense.get("category", "Other")
            amount = expense.get("amount", 0)
            category_spending[category] = category_spending.get(category, 0) + amount
        
        # Find top categories
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate percentages
        category_percentages = {}
        for category, amount in category_spending.items():
            category_percentages[category] = (amount / total_spending * 100) if total_spending > 0 else 0
        
        # Generate insights
        insights = []
        
        # High spending categories
        if sorted_categories:
            top_category, top_amount = sorted_categories[0]
            top_percentage = category_percentages[top_category]
            if top_percentage > 40:
                insights.append(f"High spending in {top_category} ({top_percentage:.1f}% of total)")
        
        # Small frequent expenses
        small_expenses = [exp for exp in expenses if exp.get("amount", 0) < 20]
        if len(small_expenses) > len(expenses) * 0.6:
            small_total = sum(exp.get("amount", 0) for exp in small_expenses)
            insights.append(f"Many small expenses totaling ${small_total:.2f}")
        
        # Recent spending trend (if timestamps available)
        recent_expenses = []
        old_expenses = []
        current_time = datetime.now()
        
        for expense in expenses:
            # Try to parse date if available
            exp_date = None
            if "date" in expense:
                try:
                    if isinstance(expense["date"], str):
                        exp_date = datetime.fromisoformat(expense["date"].replace("Z", "+00:00"))
                    elif isinstance(expense["date"], datetime):
                        exp_date = expense["date"]
                except:
                    pass
            
            if exp_date:
                days_ago = (current_time - exp_date).days
                if days_ago <= 7:
                    recent_expenses.append(expense)
                elif days_ago <= 30:
                    old_expenses.append(expense)
        
        # Trend analysis
        trends = {}
        if recent_expenses and old_expenses:
            recent_total = sum(exp.get("amount", 0) for exp in recent_expenses)
            old_total = sum(exp.get("amount", 0) for exp in old_expenses)
            
            # Calculate weekly averages
            recent_weekly = recent_total
            old_weekly = old_total / 3  # Approximate weeks in a month
            
            if old_weekly > 0:
                trend_change = ((recent_weekly - old_weekly) / old_weekly) * 100
                trends["weekly_change"] = trend_change
                
                if abs(trend_change) > 20:
                    direction = "increased" if trend_change > 0 else "decreased"
                    insights.append(f"Spending has {direction} by {abs(trend_change):.1f}% recently")
        
        return {
            "total": total_spending,
            "categories": category_spending,
            "category_percentages": category_percentages,
            "top_categories": sorted_categories[:5],
            "trends": trends,
            "insights": insights,
            "expense_count": len(expenses),
            "average_expense": total_spending / len(expenses) if expenses else 0
        }
    
    def _prepare_advice_context(self, spending_analysis: Dict, user_profile: Dict, advice_type: str) -> Dict:
        """Prepare context for advice generation"""
        
        context = {
            "spending_total": spending_analysis["total"],
            "top_categories": spending_analysis["top_categories"][:3],
            "insights": spending_analysis["insights"],
            "expense_count": spending_analysis["expense_count"],
            "average_expense": spending_analysis["average_expense"],
            "advice_type": advice_type
        }
        
        # Add user profile information if available
        if user_profile:
            context.update({
                "monthly_income": user_profile.get("monthly_income"),
                "financial_goals": user_profile.get("goals", []),
                "risk_tolerance": user_profile.get("risk_tolerance", "moderate"),
                "age": user_profile.get("age"),
                "debt": user_profile.get("debt", 0)
            })
        
        return context
    
    def _create_advice_prompt(self, context: Dict, advice_type: str) -> str:
        """Create a targeted prompt for the AI based on advice type"""
        
        base_info = f"""
        User's spending summary:
        - Total spending: ${context['spending_total']:.2f}
        - Number of expenses: {context['expense_count']}
        - Average expense: ${context['average_expense']:.2f}
        - Top spending categories: {', '.join([f"{cat}: ${amt:.2f}" for cat, amt in context['top_categories']])}
        - Key insights: {'; '.join(context['insights']) if context['insights'] else 'No specific patterns identified'}
        """
        
        if context.get("monthly_income"):
            base_info += f"\n- Monthly income: ${context['monthly_income']:.2f}"
        
        if context.get("financial_goals"):
            base_info += f"\n- Financial goals: {', '.join(context['financial_goals'])}"
        
        prompt_templates = {
            "general": f"""
            {base_info}
            
            Please provide general financial advice focusing on:
            1. Overall spending patterns and areas for improvement
            2. Budget optimization suggestions
            3. One specific actionable recommendation
            
            Keep the advice practical, encouraging, and specific to their spending patterns.
            """,
            
            "budget": f"""
            {base_info}
            
            Please provide budget-specific advice focusing on:
            1. Optimal budget allocation based on their spending patterns
            2. Categories where they could reduce spending
            3. Suggested budget limits for their top spending categories
            
            Provide specific dollar amounts and percentages where possible.
            """,
            
            "savings": f"""
            {base_info}
            
            Please provide savings-focused advice:
            1. Identify opportunities to save money from their current spending
            2. Suggest a realistic savings goal based on their expenses
            3. Recommend specific strategies to increase savings
            
            Focus on practical ways to save without drastically changing their lifestyle.
            """,
            
            "optimization": f"""
            {base_info}
            
            Please provide spending optimization advice:
            1. Identify inefficient spending patterns
            2. Suggest ways to get better value from their expenses
            3. Recommend tools or strategies to optimize their spending
            
            Focus on maximizing value rather than just cutting expenses.
            """
        }
        
        return prompt_templates.get(advice_type, prompt_templates["general"])
    
    def _structure_advice_response(self, advice_text: str, spending_analysis: Dict, advice_type: str) -> Dict:
        """Structure the AI advice into a useful format"""
        
        return {
            "advice_type": advice_type,
            "main_advice": advice_text,
            "key_insights": spending_analysis["insights"],
            "spending_summary": {
                "total": spending_analysis["total"],
                "top_category": spending_analysis["top_categories"][0] if spending_analysis["top_categories"] else None,
                "category_count": len(spending_analysis["categories"]),
                "average_expense": spending_analysis["average_expense"]
            },
            "action_items": self._extract_action_items(advice_text),
            "confidence": 0.85,  # High confidence for AI-generated advice
            "generated_at": datetime.now().isoformat(),
            "processing_method": "groq_ai"
        }
    
    def _extract_action_items(self, advice_text: str) -> List[str]:
        """Extract actionable items from the advice text"""
        
        # Simple extraction based on common patterns
        action_items = []
        lines = advice_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered lists, bullet points, or action-oriented phrases
            if (line.startswith(('1.', '2.', '3.', '-', '•')) or 
                any(word in line.lower() for word in ['consider', 'try', 'reduce', 'increase', 'set up', 'create'])):
                if len(line) > 10:  # Ignore very short lines
                    action_items.append(line)
        
        return action_items[:5]  # Limit to top 5 action items
    
    def _generate_fallback_advice(self, spending_analysis: Dict, user_profile: Dict, advice_type: str) -> Dict:
        """Generate advice when Groq API is unavailable"""
        
        total = spending_analysis["total"]
        top_categories = spending_analysis["top_categories"]
        
        # Generate rule-based advice
        advice_parts = []
        action_items = []
        
        if top_categories:
            top_cat, top_amount = top_categories[0]
            percentage = (top_amount / total * 100) if total > 0 else 0
            
            if percentage > 50:
                advice_parts.append(f"Your spending is heavily concentrated in {top_cat} ({percentage:.1f}% of total). Consider diversifying your expenses or finding ways to reduce costs in this category.")
                action_items.append(f"Review your {top_cat} expenses for potential savings")
            
            if len(top_categories) >= 2:
                second_cat, second_amount = top_categories[1]
                advice_parts.append(f"Your top two spending categories are {top_cat} (${top_amount:.2f}) and {second_cat} (${second_amount:.2f}).")
        
        # General advice based on total spending
        avg_expense = spending_analysis["average_expense"]
        if avg_expense > 100:
            advice_parts.append("You tend to make larger purchases. Consider tracking these more carefully and planning for them in your budget.")
            action_items.append("Create a budget category for large expenses")
        elif avg_expense < 10:
            advice_parts.append("You have many small expenses. These can add up quickly - consider setting a daily spending limit.")
            action_items.append("Track daily small expenses more carefully")
        
        # Add insights
        if spending_analysis["insights"]:
            advice_parts.extend(spending_analysis["insights"])
        
        main_advice = " ".join(advice_parts) if advice_parts else "Continue tracking your expenses to identify patterns and opportunities for improvement."
        
        return {
            "advice_type": advice_type,
            "main_advice": main_advice,
            "key_insights": spending_analysis["insights"],
            "spending_summary": {
                "total": total,
                "top_category": top_categories[0] if top_categories else None,
                "category_count": len(spending_analysis["categories"]),
                "average_expense": avg_expense
            },
            "action_items": action_items,
            "confidence": 0.6,  # Lower confidence for rule-based advice
            "generated_at": datetime.now().isoformat(),
            "processing_method": "rule_based_fallback"
        }
    
    def _generate_error_fallback_advice(self) -> Dict:
        """Generate basic advice when all methods fail"""
        
        return {
            "advice_type": "general",
            "main_advice": "Keep tracking your expenses regularly to understand your spending patterns. Focus on your largest expense categories first for potential savings.",
            "key_insights": [],
            "spending_summary": {},
            "action_items": [
                "Continue tracking all expenses",
                "Review monthly spending patterns",
                "Set up a basic budget"
            ],
            "confidence": 0.3,
            "generated_at": datetime.now().isoformat(),
            "processing_method": "error_fallback"
        }
    
    def _create_cache_key(self, expenses: List[Dict], user_profile: Dict, advice_type: str) -> str:
        """Create a cache key for advice requests"""
        
        # Create a simple hash of the input data
        key_data = {
            "expense_count": len(expenses),
            "total_amount": sum(exp.get("amount", 0) for exp in expenses),
            "categories": sorted(set(exp.get("category", "Other") for exp in expenses)),
            "advice_type": advice_type,
            "profile_keys": sorted(user_profile.keys()) if user_profile else []
        }
        
        return str(hash(json.dumps(key_data, sort_keys=True)))
    
    def get_advisor_stats(self) -> Dict:
        """Get performance statistics for the advisor"""
        return self.advice_stats.copy()
    
    async def generate_spending_insights(self, expenses: List[Dict]) -> Dict:
        """Generate detailed spending insights and patterns"""
        
        analysis = self._analyze_spending_patterns(expenses)
        
        # Enhanced insights
        insights = {
            "spending_velocity": self._calculate_spending_velocity(expenses),
            "category_diversity": len(analysis["categories"]),
            "spending_consistency": self._calculate_spending_consistency(expenses),
            "unusual_expenses": self._identify_unusual_expenses(expenses),
            "recommendations": []
        }
        
        # Generate recommendations based on patterns
        if analysis["category_percentages"]:
            max_category = max(analysis["category_percentages"].items(), key=lambda x: x[1])
            if max_category[1] > 60:
                insights["recommendations"].append({
                    "type": "diversification",
                    "message": f"Consider diversifying spending - {max_category[0]} represents {max_category[1]:.1f}% of expenses"
                })
        
        if insights["spending_velocity"] > 10:  # More than 10 expenses per week
            insights["recommendations"].append({
                "type": "frequency",
                "message": "You make frequent purchases - consider consolidating similar expenses"
            })
        
        return insights
    
    def _calculate_spending_velocity(self, expenses: List[Dict]) -> float:
        """Calculate how frequently user makes purchases"""
        
        if not expenses:
            return 0.0
        
        # Try to calculate based on dates if available
        dates = []
        for expense in expenses:
            if "date" in expense:
                try:
                    if isinstance(expense["date"], str):
                        date = datetime.fromisoformat(expense["date"].replace("Z", "+00:00"))
                    else:
                        date = expense["date"]
                    dates.append(date)
                except:
                    pass
        
        if len(dates) >= 2:
            dates.sort()
            time_span = (dates[-1] - dates[0]).days
            if time_span > 0:
                return len(expenses) / (time_span / 7)  # Expenses per week
        
        # Fallback: assume expenses are from current month
        return len(expenses) / 4  # Expenses per week (assuming 4 weeks)
    
    def _calculate_spending_consistency(self, expenses: List[Dict]) -> float:
        """Calculate how consistent spending amounts are"""
        
        amounts = [exp.get("amount", 0) for exp in expenses if exp.get("amount", 0) > 0]
        
        if len(amounts) < 2:
            return 1.0
        
        # Calculate coefficient of variation (lower = more consistent)
        import statistics
        mean_amount = statistics.mean(amounts)
        std_amount = statistics.stdev(amounts)
        
        if mean_amount == 0:
            return 0.0
        
        cv = std_amount / mean_amount
        
        # Convert to consistency score (0-1, higher = more consistent)
        return max(0, 1 - min(cv, 2) / 2)
    
    def _identify_unusual_expenses(self, expenses: List[Dict]) -> List[Dict]:
        """Identify expenses that are unusual in amount or category"""
        
        amounts = [exp.get("amount", 0) for exp in expenses if exp.get("amount", 0) > 0]
        
        if not amounts:
            return []
        
        # Calculate statistical outliers
        import statistics
        
        try:
            mean_amount = statistics.mean(amounts)
            std_amount = statistics.stdev(amounts)
            threshold = mean_amount + (2 * std_amount)  # 2 standard deviations
            
            unusual = []
            for expense in expenses:
                amount = expense.get("amount", 0)
                if amount > threshold:
                    unusual.append({
                        "expense": expense,
                        "reason": f"Amount ${amount:.2f} is unusually high (avg: ${mean_amount:.2f})",
                        "type": "high_amount"
                    })
            
            return unusual[:5]  # Return top 5 unusual expenses
            
        except statistics.StatisticsError:
            return []

# Global instance
financial_advisor = EnhancedFinancialAdvisor()

# Convenience functions
async def get_financial_advice(expenses: List[Dict], user_profile: Dict = None, advice_type: str = "general") -> Dict:
    """Get financial advice for a user's expenses"""
    return await financial_advisor.generate_financial_advice(expenses, user_profile, advice_type)

async def get_spending_insights(expenses: List[Dict]) -> Dict:
    """Get detailed spending insights"""
    return await financial_advisor.generate_spending_insights(expenses)
