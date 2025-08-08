"""
Enhanced AI-powered financial advisor service for Budget Tracker.
Provides personalized financial advice using Groq LLM and spending analysis.
"""

import logging
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFinancialAdvisor:
    """
    Advanced financial advisor using AI and data analysis:
    1. Groq LLM integration for personalized advice
    2. Spending pattern analysis and insights
    3. Budget optimization recommendations
    4. Financial goal tracking and predictions
    5. Smart caching and fallback responses
    """
    
    def __init__(self):
        """Initialize the enhanced financial advisor."""
        self.groq_client = None
        self.advice_cache = {}
        self.analysis_cache = {}
        self.advice_stats = {
            "total_requests": 0,
            "ai_generated": 0,
            "cache_hits": 0,
            "fallback_used": 0
        }
        
        self._initialize_groq_client()
        self._initialize_financial_knowledge()
    
    def _initialize_groq_client(self):
        """Initialize Groq client for AI-powered advice generation."""
        try:
            from groq import Groq
            
            # Get API key from environment
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                logger.warning("⚠️ GROQ_API_KEY not found in environment variables")
                return
            
            self.groq_client = Groq(api_key=api_key)
            logger.info("✅ Groq client initialized successfully")
            
        except ImportError:
            logger.warning("⚠️ Groq package not available, using fallback responses")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize Groq client: {e}")
    
    def _initialize_financial_knowledge(self):
        """Initialize financial knowledge base and templates."""
        self.financial_rules = {
            "emergency_fund": {
                "target_months": 6,
                "priority": "high",
                "description": "Build emergency fund covering 6 months of expenses"
            },
            "debt_to_income": {
                "max_ratio": 0.36,
                "warning_ratio": 0.28,
                "description": "Keep total debt payments under 36% of income"
            },
            "savings_rate": {
                "target_rate": 0.20,
                "minimum_rate": 0.10,
                "description": "Save at least 20% of income"
            },
            "housing_costs": {
                "max_ratio": 0.28,
                "description": "Housing costs should not exceed 28% of income"
            }
        }
        
        self.spending_insights = {
            "high_dining": "Consider meal planning and cooking at home to reduce dining expenses",
            "high_transportation": "Look into carpooling, public transport, or bike commuting",
            "high_entertainment": "Set a monthly entertainment budget and stick to it",
            "high_shopping": "Implement a 24-hour waiting period before non-essential purchases",
            "irregular_patterns": "Consider setting up automatic savings to smooth out spending",
            "increasing_trend": "Review recent purchases to identify spending triggers"
        }
        
        self.advice_templates = {
            "budget_optimization": [
                "Based on your spending patterns, here are some optimization opportunities:",
                "Your spending analysis reveals these key insights:",
                "To improve your financial health, consider these recommendations:"
            ],
            "category_specific": {
                "Food & Dining": [
                    "Meal planning can reduce food expenses by 15-25%",
                    "Consider cooking at home more often to save money",
                    "Look for grocery store deals and use coupons"
                ],
                "Transportation": [
                    "Compare gas prices using apps like GasBuddy",
                    "Consider carpooling or public transport for regular commutes",
                    "Maintain your vehicle regularly to improve fuel efficiency"
                ],
                "Entertainment": [
                    "Look for free community events and activities",
                    "Consider sharing streaming subscriptions with family",
                    "Set a monthly entertainment budget and track it"
                ]
            }
        }
    
    def generate_advice(self, spending_data: Dict[str, Any], user_goals: Optional[List[str]] = None, use_ai: bool = True) -> str:
        """
        Generate personalized financial advice based on spending data.
        
        Args:
            spending_data: Dictionary containing spending information
            user_goals: Optional list of user financial goals
            use_ai: Whether to use AI (Groq) for advice generation
            
        Returns:
            Personalized financial advice as string
        """
        self.advice_stats["total_requests"] += 1
        
        # Create cache key
        cache_key = self._create_cache_key(spending_data, user_goals)
        
        # Check cache first
        if cache_key in self.advice_cache:
            self.advice_stats["cache_hits"] += 1
            return self.advice_cache[cache_key]
        
        # Generate advice
        if use_ai and self.groq_client:
            advice = self._generate_ai_advice(spending_data, user_goals)
            if advice:
                self.advice_stats["ai_generated"] += 1
            else:
                advice = self._generate_fallback_advice(spending_data, user_goals)
                self.advice_stats["fallback_used"] += 1
        else:
            advice = self._generate_fallback_advice(spending_data, user_goals)
            self.advice_stats["fallback_used"] += 1
        
        # Cache the result
        self.advice_cache[cache_key] = advice
        
        return advice
    
    def _generate_ai_advice(self, spending_data: Dict[str, Any], user_goals: Optional[List[str]]) -> Optional[str]:
        """Generate advice using Groq AI."""
        try:
            # Prepare spending analysis
            analysis = self.analyze_spending_patterns(spending_data)
            
            # Create detailed prompt
            prompt = self._create_financial_prompt(spending_data, analysis, user_goals)
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": "You are an expert financial advisor. Provide practical, actionable advice based on spending data. Be encouraging but realistic. Keep advice concise and specific."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                model="llama3-8b-8192",  # Fast Groq model
                temperature=0.7,
                max_tokens=500
            )
            
            advice = response.choices[0].message.content.strip()
            logger.info("✅ AI advice generated successfully")
            return advice
            
        except Exception as e:
            logger.warning(f"⚠️ AI advice generation failed: {e}")
            return None
    
    def _create_financial_prompt(self, spending_data: Dict[str, Any], analysis: Dict[str, Any], user_goals: Optional[List[str]]) -> str:
        """Create a detailed prompt for AI advice generation."""
        total_spending = spending_data.get("total_spending", 0)
        monthly_income = spending_data.get("monthly_income", 0)
        categories = spending_data.get("categories", {})
        
        # Calculate key metrics
        savings_rate = max(0, (monthly_income - total_spending) / monthly_income) if monthly_income > 0 else 0
        spending_ratio = total_spending / monthly_income if monthly_income > 0 else 0
        
        prompt = f"""
        Analyze this user's financial situation and provide personalized advice:

        INCOME & SPENDING:
        • Monthly Income: ${monthly_income:,.2f}
        • Total Monthly Spending: ${total_spending:,.2f}
        • Savings Rate: {savings_rate:.1%}
        • Spending Ratio: {spending_ratio:.1%}

        SPENDING BY CATEGORY:
        """
        
        # Add category breakdown
        for category, amount in categories.items():
            percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
            prompt += f"• {category}: ${amount:,.2f} ({percentage:.1f}%)\n        "
        
        # Add analysis insights
        insights = analysis.get("insights", [])
        if insights:
            prompt += f"\n        SPENDING INSIGHTS:\n        "
            for insight in insights[:3]:  # Top 3 insights
                prompt += f"• {insight}\n        "
        
        # Add user goals if provided
        if user_goals:
            prompt += f"\n        USER GOALS:\n        "
            for goal in user_goals:
                prompt += f"• {goal}\n        "
        
        prompt += """
        
        Please provide:
        1. Overall financial health assessment
        2. Top 3 specific recommendations for improvement
        3. One actionable step they can take this week
        4. Encouragement and motivation
        
        Keep the advice practical, specific, and encouraging.
        """
        
        return prompt
    
    def _generate_fallback_advice(self, spending_data: Dict[str, Any], user_goals: Optional[List[str]]) -> str:
        """Generate rule-based advice when AI is not available."""
        total_spending = spending_data.get("total_spending", 0)
        monthly_income = spending_data.get("monthly_income", 0)
        categories = spending_data.get("categories", {})
        
        advice_parts = []
        
        # Overall financial health
        if monthly_income > 0:
            savings_rate = (monthly_income - total_spending) / monthly_income
            if savings_rate >= 0.20:
                advice_parts.append("🎉 Excellent! You're saving over 20% of your income.")
            elif savings_rate >= 0.10:
                advice_parts.append("👍 Good job saving! Try to increase your savings rate to 20%.")
            elif savings_rate > 0:
                advice_parts.append("💡 You're saving some money, but aim for at least 10% of income.")
            else:
                advice_parts.append("⚠️ You're spending more than you earn. Time to review your budget!")
        
        # Category-specific advice
        if categories:
            total_spending = sum(categories.values())
            for category, amount in categories.items():
                percentage = (amount / total_spending) * 100
                
                if category == "Food & Dining" and percentage > 25:
                    advice_parts.append("🍽️ Food costs are high (>25%). Try meal planning and cooking at home.")
                elif category == "Transportation" and percentage > 20:
                    advice_parts.append("🚗 Transportation costs are high (>20%). Consider carpooling or public transport.")
                elif category == "Entertainment" and percentage > 15:
                    advice_parts.append("🎬 Entertainment spending is high (>15%). Set a monthly budget for fun activities.")
        
        # General recommendations
        advice_parts.extend([
            "💰 Quick Win: Review your subscriptions and cancel unused services.",
            "📊 Track your spending daily to stay aware of your habits.",
            "🎯 Set specific financial goals and review them monthly."
        ])
        
        # Combine advice
        if not advice_parts:
            return "Keep tracking your expenses and look for ways to optimize your spending!"
        
        return "\n\n".join(advice_parts)
    
    def analyze_spending_patterns(self, spending_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze spending patterns and generate insights.
        
        Args:
            spending_data: Dictionary containing spending information
            
        Returns:
            Analysis results with insights and recommendations
        """
        cache_key = f"analysis_{hash(str(spending_data))}"
        
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        total_spending = spending_data.get("total_spending", 0)
        monthly_income = spending_data.get("monthly_income", 0)
        categories = spending_data.get("categories", {})
        
        analysis = {
            "total_spending": total_spending,
            "monthly_income": monthly_income,
            "insights": [],
            "recommendations": [],
            "metrics": {},
            "category_analysis": {}
        }
        
        # Calculate key metrics
        if monthly_income > 0:
            savings_rate = (monthly_income - total_spending) / monthly_income
            spending_ratio = total_spending / monthly_income
            
            analysis["metrics"] = {
                "savings_rate": savings_rate,
                "spending_ratio": spending_ratio,
                "disposable_income": monthly_income - total_spending
            }
            
            # Generate insights based on metrics
            if savings_rate < 0:
                analysis["insights"].append("⚠️ You're spending more than you earn")
            elif savings_rate < 0.10:
                analysis["insights"].append("💡 Your savings rate is below the recommended 10%")
            elif savings_rate >= 0.20:
                analysis["insights"].append("🎉 Excellent savings rate! You're building wealth")
        
        # Analyze spending by category
        if categories and total_spending > 0:
            for category, amount in categories.items():
                percentage = (amount / total_spending) * 100
                
                analysis["category_analysis"][category] = {
                    "amount": amount,
                    "percentage": percentage,
                    "assessment": self._assess_category_spending(category, percentage)
                }
                
                # Generate category-specific insights
                if percentage > 30:
                    analysis["insights"].append(f"📊 {category} dominates your spending ({percentage:.1f}%)")
                elif percentage > 20:
                    analysis["insights"].append(f"📈 {category} is a major expense category ({percentage:.1f}%)")
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        # Cache the analysis
        self.analysis_cache[cache_key] = analysis
        
        return analysis
    
    def _assess_category_spending(self, category: str, percentage: float) -> str:
        """Assess if spending in a category is reasonable."""
        # Benchmark percentages for different categories
        benchmarks = {
            "Food & Dining": 15,
            "Transportation": 15,
            "Entertainment": 10,
            "Utilities & Bills": 10,
            "Shopping": 10,
            "Health & Fitness": 5,
            "Travel": 10,
            "Education": 5,
            "Miscellaneous": 10
        }
        
        benchmark = benchmarks.get(category, 10)
        
        if percentage <= benchmark:
            return "optimal"
        elif percentage <= benchmark * 1.5:
            return "acceptable"
        else:
            return "high"
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on analysis."""
        recommendations = []
        
        metrics = analysis.get("metrics", {})
        category_analysis = analysis.get("category_analysis", {})
        
        # Savings rate recommendations
        savings_rate = metrics.get("savings_rate", 0)
        if savings_rate < 0.10:
            recommendations.append("Increase your savings rate to at least 10% of income")
        elif savings_rate < 0.20:
            recommendations.append("Try to boost your savings rate to 20% for better financial security")
        
        # Category-specific recommendations
        for category, data in category_analysis.items():
            if data["assessment"] == "high":
                if category == "Food & Dining":
                    recommendations.append("Reduce dining out costs by meal planning and cooking at home")
                elif category == "Transportation":
                    recommendations.append("Consider alternative transportation to reduce costs")
                elif category == "Entertainment":
                    recommendations.append("Set a monthly entertainment budget to control spending")
                elif category == "Shopping":
                    recommendations.append("Implement a 24-hour waiting period for non-essential purchases")
        
        # General recommendations
        if len(recommendations) < 3:
            general_recs = [
                "Review and optimize your monthly subscriptions",
                "Set up automatic transfers to your savings account",
                "Track your daily expenses to improve awareness",
                "Create an emergency fund covering 3-6 months of expenses",
                "Consider increasing your income through side hustles or skill development"
            ]
            
            needed = 3 - len(recommendations)
            recommendations.extend(general_recs[:needed])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _create_cache_key(self, spending_data: Dict[str, Any], user_goals: Optional[List[str]]) -> str:
        """Create a cache key for advice requests."""
        # Create a hash of the input data
        data_str = json.dumps(spending_data, sort_keys=True)
        goals_str = json.dumps(user_goals or [], sort_keys=True)
        combined = f"{data_str}_{goals_str}"
        
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def get_advice_stats(self) -> Dict[str, Any]:
        """Get advice generation statistics."""
        total = self.advice_stats["total_requests"]
        if total == 0:
            return self.advice_stats
        
        stats = self.advice_stats.copy()
        stats["ai_percentage"] = (stats["ai_generated"] / total) * 100
        stats["cache_hit_rate"] = (stats["cache_hits"] / total) * 100
        stats["fallback_percentage"] = (stats["fallback_used"] / total) * 100
        
        return stats
    
    def clear_cache(self):
        """Clear advice and analysis cache."""
        self.advice_cache.clear()
        self.analysis_cache.clear()
        logger.info("✅ Advice cache cleared")
    
    def export_analysis(self, user_id: str, spending_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export comprehensive financial analysis for a user."""
        analysis = self.analyze_spending_patterns(spending_data)
        advice = self.generate_advice(spending_data, use_ai=False)  # Use fallback for export
        
        return {
            "user_id": user_id,
            "analysis_date": datetime.now().isoformat(),
            "spending_data": spending_data,
            "analysis": analysis,
            "advice": advice,
            "stats": self.get_advice_stats()
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize advisor
    advisor = EnhancedFinancialAdvisor()
    
    # Test spending data
    test_spending_data = {
        "total_spending": 2450.00,
        "monthly_income": 5000.00,
        "categories": {
            "Food & Dining": 650.00,
            "Transportation": 420.00,
            "Entertainment": 180.00,
            "Utilities & Bills": 275.00,
            "Shopping": 380.00,
            "Health & Fitness": 95.00,
            "Miscellaneous": 450.00
        }
    }
    
    print("🧪 Testing Enhanced Financial Advisor:")
    print("-" * 50)
    
    # Test analysis
    print("📊 Spending Analysis:")
    analysis = advisor.analyze_spending_patterns(test_spending_data)
    
    print(f"💰 Total Spending: ${analysis['total_spending']:,.2f}")
    print(f"💵 Monthly Income: ${analysis['monthly_income']:,.2f}")
    print(f"📈 Savings Rate: {analysis['metrics']['savings_rate']:.1%}")
    
    print("\n🔍 Insights:")
    for insight in analysis["insights"]:
        print(f"  • {insight}")
    
    print("\n💡 Recommendations:")
    for rec in analysis["recommendations"]:
        print(f"  • {rec}")
    
    # Test advice generation
    print("\n🎯 Financial Advice:")
    advice = advisor.generate_advice(test_spending_data, use_ai=False)
    print(advice)
    
    print("\n📊 Advisor Statistics:")
    stats = advisor.get_advice_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
