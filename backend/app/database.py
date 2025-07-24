"""
Database service for AI Budget Tracker

Simple database connection setup following Railway deployment patterns.
Based on successful Journal Summarizer architecture.
"""

import os
import asyncpg
from typing import Optional, Dict, List
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """Simple database service for Railway PostgreSQL"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
        
    async def init_pool(self):
        """Initialize connection pool"""
        try:
            if self.database_url:
                # Railway provides DATABASE_URL directly
                self.pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
                logger.info("✅ Database pool initialized successfully")
                return True
            else:
                logger.warning("⚠️ DATABASE_URL not found - running in demo mode")
                return False
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    async def check_connection(self) -> bool:
        """Check if database is connected"""
        try:
            if not self.pool:
                return False
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def create_tables_if_not_exist(self):
        """Create tables if they don't exist (simplified)"""
        try:
            if not self.pool:
                logger.warning("No database pool - skipping table creation")
                return False
                
            async with self.pool.acquire() as conn:
                # Simple user table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Simple expenses table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        amount DECIMAL(10,2) NOT NULL,
                        description TEXT,
                        category VARCHAR(100),
                        expense_date DATE DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                logger.info("✅ Database tables verified/created")
                return True
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
            return False
    
    async def get_demo_expenses(self) -> List[Dict]:
        """Return demo expenses if no database"""
        return [
            {
                "id": 1,
                "amount": 12.50,
                "description": "Coffee at Starbucks",
                "category": "Food & Dining",
                "expense_date": "2025-01-24",
                "ai_confidence": 0.95
            },
            {
                "id": 2,
                "amount": 45.00,
                "description": "Gas station fill-up",
                "category": "Transportation",
                "expense_date": "2025-01-23",
                "ai_confidence": 0.89
            },
            {
                "id": 3,
                "amount": 89.99,
                "description": "Grocery shopping",
                "category": "Food & Dining", 
                "expense_date": "2025-01-22",
                "ai_confidence": 0.92
            }
        ]
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")

# Global database instance
db_service = DatabaseService()

async def get_database():
    """Dependency injection for database service"""
    if not db_service.pool:
        await db_service.init_pool()
        await db_service.create_tables_if_not_exist()
    return db_service
