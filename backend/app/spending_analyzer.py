"""
AI-Powered Spending Analytics for Budget Tracker
Priority 3: Advanced pattern analysis and insights generation
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import json
import logging
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)

class SpendingAnalyzer:
    """Advanced spending pattern analysis with AI insights"""
    
    def __init__(self, expense_db=None):
        self.expense_db = expense_db
        self.insights_cache = {}
    
    async def analyze_spending_patterns(self, user_id: str = 'default_user', days: int = 30) -> Dict:
        """Comprehensive spending pattern analysis"""
        try:
            # Get expenses for analysis
            if self.expense_db and hasattr(self.expense_db, 'get_expenses'):
                expenses = await self.expense_db.get_expenses(user_id, limit=200)
            else:
                # Use mock data for testing
                expenses = self._generate_mock_expenses()
            
            # Filter by date range
            cutoff_date = date.today() - timedelta(days=days)
            recent_expenses = [
                exp for exp in expenses 
                if self._parse_date(exp.get('expense_date', date.today().isoformat())) >= cutoff_date
            ]
            
            analysis = {
                'period_days': days,
                'total_expenses': len(recent_expenses),
                'total_amount': sum(float(exp['amount']) for exp in recent_expenses),
                'patterns': await self._analyze_patterns(recent_expenses),
                'insights': await self._generate_insights(recent_expenses),
                'recommendations': await self._generate_recommendations(recent_expenses),
                'ai_stats': self._analyze_ai_categorization(recent_expenses),
                'trends': self._analyze_trends(recent_expenses),
                'anomalies': self._detect_anomalies(recent_expenses)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Spending analysis failed: {e}")
            return self._empty_analysis(days)
    
    async def _analyze_patterns(self, expenses: List[Dict]) -> Dict:
        """Analyze spending patterns"""
        if not expenses:
            return {}
        
        # Category analysis
        category_stats = defaultdict(lambda: {'amount': 0, 'count': 0, 'avg': 0})
        for exp in expenses:
            cat = exp['category']
            amount = float(exp['amount'])
            category_stats[cat]['amount'] += amount
            category_stats[cat]['count'] += 1
        
        # Calculate averages
        for cat_data in category_stats.values():
            cat_data['avg'] = cat_data['amount'] / cat_data['count']
        
        # Day of week patterns
        day_patterns = defaultdict(lambda: {'amount': 0, 'count': 0})
        for exp in expenses:
            exp_date = self._parse_date(exp.get('expense_date'))
            day_name = exp_date.strftime('%A')
            day_patterns[day_name]['amount'] += float(exp['amount'])
            day_patterns[day_name]['count'] += 1
        
        # Spending frequency analysis
        amounts = [float(exp['amount']) for exp in expenses]
        frequency_analysis = {
            'avg_transaction': statistics.mean(amounts) if amounts else 0,
            'median_transaction': statistics.median(amounts) if amounts else 0,
            'max_transaction': max(amounts) if amounts else 0,
            'min_transaction': min(amounts) if amounts else 0,
            'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0
        }
        
        return {
            'categories': dict(category_stats),
            'day_patterns': dict(day_patterns),
            'frequency_analysis': frequency_analysis,
            'top_categories': sorted(
                category_stats.items(),
                key=lambda x: x[1]['amount'],
                reverse=True
            )[:5]
        }
    
    async def _generate_insights(self, expenses: List[Dict]) -> List[Dict]:
        """Generate AI-powered financial insights"""
        insights = []
        
        if not expenses:
            return insights
        
        # Insight 1: Spending velocity
        total_amount = sum(float(exp['amount']) for exp in expenses)
        daily_avg = total_amount / 30 if expenses else 0
        
        if daily_avg > 50:
            insights.append({
                'type': 'spending_velocity',
                'title': '⚡ High Daily Spending Detected',
                'content': f'You\'re averaging ${daily_avg:.2f} per day. Consider setting daily spending limits.',
                'confidence': 0.85,
                'priority': 'high',
                'action_items': [
                    'Set a daily spending budget',
                    'Track discretionary purchases',
                    'Review top spending categories'
                ]
            })
        
        # Insight 2: Category concentration
        category_amounts = defaultdict(float)
        for exp in expenses:
            category_amounts[exp['category']] += float(exp['amount'])
        
        if category_amounts:
            top_category = max(category_amounts.items(), key=lambda x: x[1])
            if top_category[1] / total_amount > 0.4:
                insights.append({
                    'type': 'category_concentration',
                    'title': f'📊 High Spending in {top_category[0]}',
                    'content': f'{top_category[0]} accounts for {(top_category[1]/total_amount)*100:.1f}% of your spending (${top_category[1]:.2f})',
                    'confidence': 0.90,
                    'priority': 'medium',
                    'action_items': [
                        f'Review {top_category[0]} expenses for optimization',
                        'Consider alternatives or bulk purchasing',
                        'Set category-specific budgets'
                    ]
                })
        
        # Insight 3: AI categorization efficiency
        ai_categorized = sum(1 for exp in expenses if exp.get('categorization_method') == 'ai_classification')
        if len(expenses) > 10:
            ai_percentage = (ai_categorized / len(expenses)) * 100
            if ai_percentage > 70:
                insights.append({
                    'type': 'ai_efficiency',
                    'title': '🤖 AI Categorization Working Well',
                    'content': f'{ai_percentage:.1f}% of expenses automatically categorized with AI',
                    'confidence': 0.95,
                    'priority': 'low',
                    'action_items': [
                        'Continue using descriptive expense names',
                        'Review and confirm AI categories occasionally'
                    ]
                })
        
        # Insight 4: Spending consistency
        amounts = [float(exp['amount']) for exp in expenses]
        if len(amounts) > 5:
            std_dev = statistics.stdev(amounts)
            mean_amount = statistics.mean(amounts)
            coefficient_variation = std_dev / mean_amount if mean_amount > 0 else 0
            
            if coefficient_variation > 2:
                insights.append({
                    'type': 'spending_variability',
                    'title': '📈 Irregular Spending Pattern',
                    'content': f'Your spending varies significantly (${std_dev:.2f} standard deviation)',
                    'confidence': 0.80,
                    'priority': 'medium',
                    'action_items': [
                        'Identify large, irregular expenses',
                        'Plan for variable expenses',
                        'Consider smoothing spending over time'
                    ]
                })
        
        return insights
    
    async def _generate_recommendations(self, expenses: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not expenses:
            return [{
                'type': 'getting_started',
                'title': '🚀 Start Tracking Your Expenses',
                'content': 'Add your daily expenses to get personalized insights and recommendations',
                'priority': 'high',
                'estimated_savings': 0
            }]
        
        # Recommendation 1: Budget allocation
        total_amount = sum(float(exp['amount']) for exp in expenses)
        category_amounts = defaultdict(float)
        for exp in expenses:
            category_amounts[exp['category']] += float(exp['amount'])
        
        if 'Food & Dining' in category_amounts and category_amounts['Food & Dining'] / total_amount > 0.3:
            recommendations.append({
                'type': 'budget_optimization',
                'title': '🍽️ Optimize Food Spending',
                'content': f'Food spending is ${category_amounts["Food & Dining"]:.2f}. Consider meal planning.',
                'priority': 'medium',
                'estimated_savings': category_amounts["Food & Dining"] * 0.15,
                'actions': [
                    'Plan meals weekly',
                    'Cook at home more often',
                    'Use grocery lists'
                ]
            })
        
        # Recommendation 2: Small recurring expenses
        small_expenses = [exp for exp in expenses if float(exp['amount']) < 10]
        if len(small_expenses) > len(expenses) * 0.6:
            total_small = sum(float(exp['amount']) for exp in small_expenses)
            recommendations.append({
                'type': 'micro_spending',
                'title': '☕ Small Expenses Add Up',
                'content': f'Small purchases (under $10) total ${total_small:.2f}',
                'priority': 'low',
                'estimated_savings': total_small * 0.2,
                'actions': [
                    'Track small daily purchases',
                    'Set weekly limits for discretionary spending',
                    'Bundle small purchases'
                ]
            })
        
        return recommendations
    
    def _analyze_ai_categorization(self, expenses: List[Dict]) -> Dict:
        """Analyze AI categorization performance"""
        if not expenses:
            return {'ai_categorized': 0, 'keyword_categorized': 0, 'manual_categorized': 0, 'average_confidence': 0}
        
        methods = Counter(exp.get('categorization_method', 'manual') for exp in expenses)
        confidences = [
            float(exp.get('category_confidence', 0)) 
            for exp in expenses 
            if exp.get('category_confidence', 0) > 0
        ]
        
        return {
            'ai_categorized': methods.get('ai_classification', 0),
            'keyword_categorized': methods.get('keyword_matching', 0),
            'manual_categorized': methods.get('manual', 0),
            'average_confidence': statistics.mean(confidences) if confidences else 0,
            'high_confidence_count': sum(1 for c in confidences if c > 0.8),
            'total_categorized': len(expenses)
        }
    
    def _analyze_trends(self, expenses: List[Dict]) -> Dict:
        """Analyze spending trends over time"""
        if not expenses:
            return {}
        
        # Group by week
        weekly_spending = defaultdict(float)
        for exp in expenses:
            exp_date = self._parse_date(exp.get('expense_date'))
            week_start = exp_date - timedelta(days=exp_date.weekday())
            weekly_spending[week_start.isoformat()] += float(exp['amount'])
        
        weeks = sorted(weekly_spending.keys())
        amounts = [weekly_spending[week] for week in weeks]
        
        trend_direction = 'stable'
        if len(amounts) > 1:
            if amounts[-1] > amounts[0] * 1.2:
                trend_direction = 'increasing'
            elif amounts[-1] < amounts[0] * 0.8:
                trend_direction = 'decreasing'
        
        return {
            'weekly_spending': weekly_spending,
            'trend_direction': trend_direction,
            'weeks_analyzed': len(weeks),
            'avg_weekly': statistics.mean(amounts) if amounts else 0
        }
    
    def _detect_anomalies(self, expenses: List[Dict]) -> List[Dict]:
        """Detect unusual spending patterns"""
        anomalies = []
        
        if len(expenses) < 5:
            return anomalies
        
        amounts = [float(exp['amount']) for exp in expenses]
        mean_amount = statistics.mean(amounts)
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        # Detect unusually large expenses
        threshold = mean_amount + (2 * std_dev)
        for exp in expenses:
            amount = float(exp['amount'])
            if amount > threshold and amount > 50:  # Only flag if also above $50
                anomalies.append({
                    'type': 'large_expense',
                    'expense': exp,
                    'amount': amount,
                    'threshold': threshold,
                    'description': f"Unusually large: ${amount:.2f} (avg: ${mean_amount:.2f})"
                })
        
        return anomalies[:5]  # Limit to top 5 anomalies
    
    def _parse_date(self, date_str) -> date:
        """Parse date string to date object"""
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, str):
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            except:
                return date.today()
        return date.today()
    
    def _generate_mock_expenses(self) -> List[Dict]:
        """Generate mock expenses for testing"""
        return [
            {
                'id': 1,
                'description': 'Starbucks Coffee',
                'amount': 5.50,
                'category': 'Food & Dining',
                'category_confidence': 0.95,
                'categorization_method': 'ai_classification',
                'expense_date': (date.today() - timedelta(days=1)).isoformat()
            },
            {
                'id': 2,
                'description': 'Grocery Store',
                'amount': 67.89,
                'category': 'Groceries',
                'category_confidence': 0.88,
                'categorization_method': 'keyword_matching',
                'expense_date': (date.today() - timedelta(days=2)).isoformat()
            },
            {
                'id': 3,
                'description': 'Gas Station',
                'amount': 45.00,
                'category': 'Transportation',
                'category_confidence': 0.92,
                'categorization_method': 'ai_classification',
                'expense_date': (date.today() - timedelta(days=3)).isoformat()
            },
            {
                'id': 4,
                'description': 'Netflix Subscription',
                'amount': 15.99,
                'category': 'Entertainment',
                'category_confidence': 0.98,
                'categorization_method': 'keyword_matching',
                'expense_date': (date.today() - timedelta(days=5)).isoformat()
            },
            {
                'id': 5,
                'description': 'Lunch at Restaurant',
                'amount': 18.75,
                'category': 'Food & Dining',
                'category_confidence': 0.87,
                'categorization_method': 'ai_classification',
                'expense_date': (date.today() - timedelta(days=7)).isoformat()
            }
        ]
    
    def _empty_analysis(self, days: int) -> Dict:
        """Return empty analysis structure"""
        return {
            'period_days': days,
            'total_expenses': 0,
            'total_amount': 0,
            'patterns': {},
            'insights': [],
            'recommendations': [],
            'ai_stats': {'ai_categorized': 0, 'keyword_categorized': 0, 'manual_categorized': 0, 'average_confidence': 0},
            'trends': {},
            'anomalies': []
        }

# Global analyzer instance
spending_analyzer = SpendingAnalyzer()
