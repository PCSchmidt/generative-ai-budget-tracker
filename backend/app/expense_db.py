"""
Database schema and operations for AI Budget Tracker
Handles expense storage with AI categorization metadata
"""

import asyncpg
import os
from typing import List, Dict, Optional
from datetime import datetime, date
import json
import logging

logger = logging.getLogger(__name__)

class ExpenseDatabase:
    """Database operations for expenses with AI categorization"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
    
    async def init_pool(self):
        """Initialize database connection pool"""
        try:
            if self.database_url:
                self.pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
                logger.info("✅ Database pool initialized")
                await self.create_tables()
                return True
            else:
                logger.warning("⚠️ DATABASE_URL not found")
                return False
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    async def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            async with self.pool.acquire() as conn:
                # Create expenses table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS expenses (
                        id SERIAL PRIMARY KEY,
                        description TEXT NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        category_confidence DECIMAL(3,2) DEFAULT 0.0,
                        categorization_method VARCHAR(50) DEFAULT 'manual',
                        
                        -- Timestamps
                        date_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        expense_date DATE DEFAULT CURRENT_DATE,
                        
                        -- User and session (for future multi-user support)
                        user_id VARCHAR(100) DEFAULT 'default_user',
                        session_id VARCHAR(100),
                        
                        -- Additional metadata
                        notes TEXT,
                        is_recurring BOOLEAN DEFAULT FALSE,
                        tags JSONB,
                        ai_data JSONB  -- Store full AI categorization response
                    )
                ''')
                
                # Create indexes separately
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_expenses_expense_date ON expenses(expense_date)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date_created ON expenses(date_created)')
                
                # Create budgets table (for future use)
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS budgets (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(100) DEFAULT 'default_user',
                        category VARCHAR(100) NOT NULL,
                        budget_amount DECIMAL(10,2) NOT NULL,
                        period VARCHAR(20) DEFAULT 'monthly',
                        start_date DATE DEFAULT CURRENT_DATE,
                        end_date DATE,
                        is_active BOOLEAN DEFAULT TRUE,
                        date_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create insights table for AI-generated insights
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS financial_insights (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(100) DEFAULT 'default_user',
                        insight_type VARCHAR(100) NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        content TEXT NOT NULL,
                        confidence_score DECIMAL(3,2) DEFAULT 0.0,
                        data_period_start DATE,
                        data_period_end DATE,
                        expenses_analyzed INTEGER DEFAULT 0,
                        date_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE,
                        is_archived BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                logger.info("✅ Database tables created/verified")
                
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
            raise
    
    async def create_expense(self, expense_data: Dict) -> Dict:
        """Create a new expense record"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow('''
                    INSERT INTO expenses (
                        description, amount, category, category_confidence,
                        categorization_method, expense_date, user_id, ai_data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id, description, amount, category, category_confidence,
                             categorization_method, date_created, expense_date, user_id
                ''', 
                    expense_data['description'],
                    float(expense_data['amount']),
                    expense_data['category'],
                    expense_data.get('category_confidence', 0.0),
                    expense_data.get('categorization_method', 'manual'),
                    expense_data.get('expense_date', date.today()),
                    expense_data.get('user_id', 'default_user'),
                    json.dumps(expense_data.get('ai_data', {}))
                )
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ Create expense failed: {e}")
            raise
    
    async def get_expenses(self, user_id: str = 'default_user', limit: int = 50) -> List[Dict]:
        """Get expenses for a user"""
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch('''
                    SELECT id, description, amount, category, category_confidence,
                           categorization_method, date_created, expense_date, user_id,
                           notes, is_recurring, tags, ai_data
                    FROM expenses 
                    WHERE user_id = $1
                    ORDER BY date_created DESC
                    LIMIT $2
                ''', user_id, limit)
                
                expenses = []
                for row in results:
                    expense = dict(row)
                    # Parse JSON fields
                    expense['ai_data'] = json.loads(expense['ai_data']) if expense['ai_data'] else {}
                    expense['tags'] = expense['tags'] if expense['tags'] else []
                    # Convert timestamps to ISO strings
                    expense['date_created'] = expense['date_created'].isoformat()
                    expense['expense_date'] = expense['expense_date'].isoformat()
                    expenses.append(expense)
                
                return expenses
                
        except Exception as e:
            logger.error(f"❌ Get expenses failed: {e}")
            return []
    
    async def get_expense_by_id(self, expense_id: int, user_id: str = 'default_user') -> Optional[Dict]:
        """Get a specific expense by ID"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow('''
                    SELECT * FROM expenses 
                    WHERE id = $1 AND user_id = $2
                ''', expense_id, user_id)
                
                if result:
                    expense = dict(result)
                    expense['ai_data'] = json.loads(expense['ai_data']) if expense['ai_data'] else {}
                    expense['tags'] = expense['tags'] if expense['tags'] else []
                    expense['date_created'] = expense['date_created'].isoformat()
                    expense['expense_date'] = expense['expense_date'].isoformat()
                    return expense
                return None
                
        except Exception as e:
            logger.error(f"❌ Get expense by ID failed: {e}")
            return None
    
    async def update_expense(self, expense_id: int, updates: Dict, user_id: str = 'default_user') -> bool:
        """Update an expense"""
        try:
            async with self.pool.acquire() as conn:
                # Build dynamic update query
                set_clauses = []
                values = []
                param_num = 1
                
                for field, value in updates.items():
                    if field in ['description', 'amount', 'category', 'category_confidence', 
                               'categorization_method', 'notes', 'is_recurring']:
                        set_clauses.append(f"{field} = ${param_num}")
                        values.append(value)
                        param_num += 1
                
                if not set_clauses:
                    return False
                
                query = f'''
                    UPDATE expenses 
                    SET {', '.join(set_clauses)}
                    WHERE id = ${param_num} AND user_id = ${param_num + 1}
                '''
                values.extend([expense_id, user_id])
                
                result = await conn.execute(query, *values)
                return result.split()[-1] == '1'  # Check if one row was updated
                
        except Exception as e:
            logger.error(f"❌ Update expense failed: {e}")
            return False
    
    async def delete_expense(self, expense_id: int, user_id: str = 'default_user') -> bool:
        """Delete an expense"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute('''
                    DELETE FROM expenses 
                    WHERE id = $1 AND user_id = $2
                ''', expense_id, user_id)
                
                return result.split()[-1] == '1'  # Check if one row was deleted
                
        except Exception as e:
            logger.error(f"❌ Delete expense failed: {e}")
            return False
    
    async def get_spending_analytics(self, user_id: str = 'default_user', days: int = 30) -> Dict:
        """Get spending analytics for insights"""
        try:
            async with self.pool.acquire() as conn:
                # Get spending by category
                category_results = await conn.fetch('''
                    SELECT category, SUM(amount) as total, COUNT(*) as count
                    FROM expenses 
                    WHERE user_id = $1 AND expense_date >= CURRENT_DATE - INTERVAL '%s days'
                    GROUP BY category
                    ORDER BY total DESC
                ''', user_id, days)
                
                # Get total spending
                total_result = await conn.fetchrow('''
                    SELECT SUM(amount) as total, COUNT(*) as count
                    FROM expenses 
                    WHERE user_id = $1 AND expense_date >= CURRENT_DATE - INTERVAL '%s days'
                ''', user_id, days)
                
                # Get AI categorization stats
                ai_stats = await conn.fetchrow('''
                    SELECT 
                        COUNT(*) FILTER (WHERE categorization_method = 'ai_classification') as ai_count,
                        COUNT(*) FILTER (WHERE categorization_method = 'keyword_matching') as keyword_count,
                        COUNT(*) FILTER (WHERE categorization_method = 'manual') as manual_count,
                        AVG(category_confidence) as avg_confidence
                    FROM expenses 
                    WHERE user_id = $1 AND expense_date >= CURRENT_DATE - INTERVAL '%s days'
                ''', user_id, days)
                
                return {
                    'total_amount': float(total_result['total']) if total_result['total'] else 0,
                    'total_expenses': total_result['count'],
                    'categories': [
                        {
                            'category': row['category'],
                            'amount': float(row['total']),
                            'count': row['count']
                        } for row in category_results
                    ],
                    'ai_stats': {
                        'ai_categorized': ai_stats['ai_count'],
                        'keyword_categorized': ai_stats['keyword_count'],
                        'manual_categorized': ai_stats['manual_count'],
                        'average_confidence': float(ai_stats['avg_confidence']) if ai_stats['avg_confidence'] else 0
                    },
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"❌ Get analytics failed: {e}")
            return {
                'total_amount': 0,
                'total_expenses': 0,
                'categories': [],
                'ai_stats': {'ai_categorized': 0, 'keyword_categorized': 0, 'manual_categorized': 0, 'average_confidence': 0},
                'period_days': days
            }

# Global database instance
expense_db = ExpenseDatabase()
