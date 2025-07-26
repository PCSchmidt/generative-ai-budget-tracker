"""
Priority 4: Data Visualization API Extensions
Enhanced endpoints for real-time chart data and dashboard analytics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
import json

# Create router for visualization endpoints
viz_router = APIRouter(prefix="/api/visualization", tags=["visualization"])

class DataVisualizationService:
    """Service for providing chart-ready data"""
    
    def __init__(self, expense_db=None, spending_analyzer=None):
        self.expense_db = expense_db
        self.spending_analyzer = spending_analyzer
    
    async def get_chart_data(self, chart_type: str, days: int = 30) -> Dict:
        """Get chart-ready data for different visualization types"""
        try:
            # Get base analytics
            if self.spending_analyzer:
                analysis = await self.spending_analyzer.analyze_spending_patterns(days=days)
            else:
                analysis = self._get_mock_analysis(days)
            
            if chart_type == "category_pie":
                return self._format_category_pie_data(analysis)
            elif chart_type == "daily_trend":
                return self._format_daily_trend_data(analysis, days)
            elif chart_type == "ai_performance":
                return self._format_ai_performance_data(analysis)
            elif chart_type == "spending_heatmap":
                return self._format_spending_heatmap_data(analysis)
            elif chart_type == "budget_vs_actual":
                return self._format_budget_comparison_data(analysis)
            elif chart_type == "category_trends":
                return self._format_category_trends_data(analysis, days)
            else:
                raise ValueError(f"Unknown chart type: {chart_type}")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chart data generation failed: {str(e)}")
    
    def _format_category_pie_data(self, analysis: Dict) -> Dict:
        """Format data for category pie chart"""
        categories = analysis.get('patterns', {}).get('categories', {})
        
        labels = []
        amounts = []
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF']
        
        for category, data in categories.items():
            labels.append(category)
            amounts.append(data['amount'])
        
        return {
            "type": "doughnut",
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": amounts,
                    "backgroundColor": colors[:len(labels)],
                    "borderWidth": 2,
                    "borderColor": "#ffffff"
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "right"},
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { return context.label + ': $' + context.parsed.toFixed(2); }"
                        }
                    }
                }
            }
        }
    
    def _format_daily_trend_data(self, analysis: Dict, days: int) -> Dict:
        """Format data for daily spending trend chart"""
        # Generate daily data for the past N days
        labels = []
        amounts = []
        
        for i in range(days, 0, -1):
            day = date.today() - timedelta(days=i)
            labels.append(day.strftime('%m/%d'))
            # Mock daily amount - in real implementation, query database by date
            amounts.append(max(0, (analysis['total_amount'] / days) + ((-1) ** i) * (i % 10)))
        
        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Daily Spending",
                    "data": amounts,
                    "borderColor": "#007bff",
                    "backgroundColor": "rgba(0, 123, 255, 0.1)",
                    "fill": True,
                    "tension": 0.4,
                    "pointBackgroundColor": "#007bff",
                    "pointBorderColor": "#ffffff",
                    "pointBorderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {"beginAtZero": True},
                    "x": {"grid": {"display": False}}
                },
                "plugins": {
                    "tooltip": {
                        "mode": "index",
                        "intersect": False
                    }
                }
            }
        }
    
    def _format_ai_performance_data(self, analysis: Dict) -> Dict:
        """Format data for AI performance chart"""
        ai_stats = analysis.get('ai_stats', {})
        
        return {
            "type": "bar",
            "data": {
                "labels": ["AI Categorized", "Keyword Match", "Manual Entry"],
                "datasets": [{
                    "label": "Number of Expenses",
                    "data": [
                        ai_stats.get('ai_categorized', 0),
                        ai_stats.get('keyword_categorized', 0),
                        ai_stats.get('manual_categorized', 0)
                    ],
                    "backgroundColor": ["#28a745", "#ffc107", "#dc3545"],
                    "borderWidth": 1,
                    "borderRadius": 8
                }]
            },
            "options": {
                "responsive": True,
                "scales": {"y": {"beginAtZero": True}},
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {
                        "callbacks": {
                            "afterLabel": f"function(context) {{ return 'Avg Confidence: {ai_stats.get('average_confidence', 0):.1%}'; }}"
                        }
                    }
                }
            }
        }
    
    def _format_spending_heatmap_data(self, analysis: Dict) -> Dict:
        """Format data for spending heatmap by day of week and hour"""
        # Mock heatmap data - in real implementation, analyze expense timestamps
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        
        heatmap_data = []
        for day_idx, day in enumerate(days):
            for hour in hours:
                # Generate mock intensity based on typical spending patterns
                intensity = 0
                if 7 <= hour <= 9:  # Morning coffee
                    intensity = 30 + (day_idx * 5)
                elif 12 <= hour <= 14:  # Lunch
                    intensity = 50 + (day_idx * 8)
                elif 18 <= hour <= 20:  # Dinner
                    intensity = 40 + (day_idx * 6)
                elif day_idx >= 5 and 10 <= hour <= 22:  # Weekend activity
                    intensity = 25 + (hour % 10)
                
                heatmap_data.append({
                    "day": day,
                    "hour": hour,
                    "value": intensity
                })
        
        return {
            "type": "heatmap",
            "data": heatmap_data,
            "options": {
                "responsive": True,
                "scales": {
                    "x": {"title": {"display": True, "text": "Hour of Day"}},
                    "y": {"title": {"display": True, "text": "Day of Week"}}
                }
            }
        }
    
    def _format_budget_comparison_data(self, analysis: Dict) -> Dict:
        """Format data for budget vs actual spending comparison"""
        categories = analysis.get('patterns', {}).get('categories', {})
        
        # Mock budget data - in real implementation, fetch from budgets table
        mock_budgets = {
            'Food & Dining': 200,
            'Transportation': 150,
            'Groceries': 300,
            'Entertainment': 100,
            'Utilities': 200,
            'Healthcare': 150
        }
        
        labels = []
        budget_amounts = []
        actual_amounts = []
        
        for category in mock_budgets.keys():
            labels.append(category)
            budget_amounts.append(mock_budgets[category])
            actual_amounts.append(categories.get(category, {}).get('amount', 0))
        
        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Budget",
                        "data": budget_amounts,
                        "backgroundColor": "rgba(54, 162, 235, 0.5)",
                        "borderColor": "rgba(54, 162, 235, 1)",
                        "borderWidth": 1
                    },
                    {
                        "label": "Actual",
                        "data": actual_amounts,
                        "backgroundColor": "rgba(255, 99, 132, 0.5)",
                        "borderColor": "rgba(255, 99, 132, 1)",
                        "borderWidth": 1
                    }
                ]
            },
            "options": {
                "responsive": True,
                "scales": {"y": {"beginAtZero": True}},
                "plugins": {
                    "tooltip": {
                        "mode": "index",
                        "intersect": False
                    }
                }
            }
        }
    
    def _format_category_trends_data(self, analysis: Dict, days: int) -> Dict:
        """Format data for category spending trends over time"""
        categories = list(analysis.get('patterns', {}).get('categories', {}).keys())
        if not categories:
            categories = ['Food & Dining', 'Transportation', 'Groceries']
        
        # Generate trend data for past weeks
        weeks = []
        datasets = []
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
        
        # Create weekly labels
        for i in range(4, 0, -1):
            week_start = date.today() - timedelta(weeks=i)
            weeks.append(f"Week of {week_start.strftime('%m/%d')}")
        
        # Create dataset for each category
        for idx, category in enumerate(categories[:5]):  # Limit to 5 categories
            category_data = []
            base_amount = analysis.get('patterns', {}).get('categories', {}).get(category, {}).get('amount', 50)
            
            for week in range(4):
                # Generate mock trend data
                trend_amount = base_amount * (0.8 + (week * 0.1) + (idx * 0.05))
                category_data.append(trend_amount)
            
            datasets.append({
                "label": category,
                "data": category_data,
                "borderColor": colors[idx % len(colors)],
                "backgroundColor": colors[idx % len(colors)] + "20",
                "fill": False,
                "tension": 0.4
            })
        
        return {
            "type": "line",
            "data": {
                "labels": weeks,
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "scales": {"y": {"beginAtZero": True}},
                "plugins": {
                    "tooltip": {
                        "mode": "index",
                        "intersect": False
                    }
                }
            }
        }
    
    def _get_mock_analysis(self, days: int) -> Dict:
        """Fallback mock analysis for when database isn't available"""
        return {
            'total_amount': 153.13,
            'total_expenses': 5,
            'patterns': {
                'categories': {
                    'Food & Dining': {'amount': 67.89, 'count': 2},
                    'Transportation': {'amount': 45.00, 'count': 1},
                    'Groceries': {'amount': 24.25, 'count': 1},
                    'Entertainment': {'amount': 15.99, 'count': 1}
                }
            },
            'ai_stats': {
                'ai_categorized': 3,
                'keyword_categorized': 2,
                'manual_categorized': 0,
                'average_confidence': 0.92
            }
        }

# Global visualization service instance
viz_service = DataVisualizationService()

# API Endpoints for Priority 4
@viz_router.get("/chart-data/{chart_type}")
async def get_chart_data(
    chart_type: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """Get chart-ready data for visualizations"""
    return await viz_service.get_chart_data(chart_type, days)

@viz_router.get("/dashboard-summary")
async def get_dashboard_summary(days: int = Query(30, ge=1, le=365)):
    """Get summary data for dashboard metrics"""
    try:
        if viz_service.spending_analyzer:
            analysis = await viz_service.spending_analyzer.analyze_spending_patterns(days=days)
        else:
            analysis = viz_service._get_mock_analysis(days)
        
        return {
            "status": "success",
            "summary": {
                "total_amount": analysis['total_amount'],
                "total_expenses": analysis['total_expenses'],
                "daily_average": analysis['total_amount'] / days,
                "ai_accuracy": analysis['ai_stats']['average_confidence'],
                "top_category": max(
                    analysis['patterns']['categories'].items(),
                    key=lambda x: x[1]['amount']
                )[0] if analysis['patterns']['categories'] else "None",
                "insights_count": len(analysis.get('insights', [])),
                "recommendations_count": len(analysis.get('recommendations', [])),
                "period_days": days
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard summary failed: {str(e)}")

@viz_router.get("/real-time-metrics")
async def get_real_time_metrics():
    """Get real-time metrics for live dashboard updates"""
    try:
        # This would connect to real-time data streams
        # For now, return current state with timestamp
        current_time = datetime.now()
        
        if viz_service.expense_db and hasattr(viz_service.expense_db, 'get_expenses'):
            # Get latest expenses
            latest_expenses = await viz_service.expense_db.get_expenses(limit=5)
            expense_count = len(latest_expenses)
            latest_amount = latest_expenses[0]['amount'] if latest_expenses else 0
        else:
            expense_count = 5
            latest_amount = 15.99
        
        return {
            "status": "success",
            "timestamp": current_time.isoformat(),
            "metrics": {
                "last_expense_amount": latest_amount,
                "total_expenses_today": expense_count,
                "system_status": "operational",
                "ai_categorization_active": True,
                "database_connected": viz_service.expense_db is not None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time metrics failed: {str(e)}")

@viz_router.get("/export-data")
async def export_visualization_data(
    format: str = Query("json", regex="^(json|csv)$"),
    days: int = Query(30, ge=1, le=365)
):
    """Export visualization data in different formats"""
    try:
        if viz_service.spending_analyzer:
            analysis = await viz_service.spending_analyzer.analyze_spending_patterns(days=days)
        else:
            analysis = viz_service._get_mock_analysis(days)
        
        if format == "json":
            return {
                "status": "success",
                "format": "json",
                "data": analysis,
                "exported_at": datetime.now().isoformat()
            }
        elif format == "csv":
            # Convert to CSV format
            csv_data = "Category,Amount,Count,Percentage\n"
            total_amount = analysis['total_amount']
            
            for category, data in analysis['patterns']['categories'].items():
                percentage = (data['amount'] / total_amount * 100) if total_amount > 0 else 0
                csv_data += f"{category},{data['amount']},{data['count']},{percentage:.1f}%\n"
            
            return {
                "status": "success",
                "format": "csv",
                "data": csv_data,
                "exported_at": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data export failed: {str(e)}")
