"""
Authentication models for AI Budget Tracker
Defines user and session models for secure authentication
"""

import asyncpg
import os
from typing import List, Dict, Optional
from datetime import datetime, date
import json
import logging
import bcrypt

logger = logging.getLogger(__name__)

class AuthModels:
    """Database operations for user authentication and sessions"""
    
    def __init__(self, pool=None):
        self.pool = pool
    
    async def create_auth_tables(self):
        """Create authentication-related tables"""
        try:
            async with self.pool.acquire() as conn:
                # Create users table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        
                        -- Account status
                        is_active BOOLEAN DEFAULT true,
                        is_verified BOOLEAN DEFAULT false,
                        
                        -- Verification and reset tokens
                        verification_token VARCHAR(255),
                        reset_token VARCHAR(255),
                        reset_token_expires TIMESTAMP WITH TIME ZONE,
                        
                        -- Timestamps
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP WITH TIME ZONE
                    )
                ''')
                
                # Create user_sessions table for refresh tokens
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        refresh_token VARCHAR(255) UNIQUE NOT NULL,
                        device_info VARCHAR(255),
                        ip_address INET,
                        user_agent TEXT,
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for performance
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_verification_token ON users(verification_token)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_reset_token ON users(reset_token)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token ON user_sessions(refresh_token)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON user_sessions(expires_at)')
                
                logger.info("✅ Authentication tables created successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to create auth tables: {e}")
            return False
    
    async def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Create a new user with hashed password"""
        try:
            async with self.pool.acquire() as conn:
                # Hash the password
                hashed_password = bcrypt.hashpw(
                    user_data['password'].encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                # Insert user
                user_id = await conn.fetchval('''
                    INSERT INTO users (
                        email, username, hashed_password, first_name, last_name,
                        verification_token
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                ''', 
                    user_data['email'],
                    user_data['username'], 
                    hashed_password,
                    user_data.get('first_name'),
                    user_data.get('last_name'),
                    user_data.get('verification_token')
                )
                
                # Return user without password
                return await self.get_user_by_id(user_id)
                
        except asyncpg.UniqueViolationError as e:
            if 'email' in str(e):
                raise ValueError("Email already registered")
            elif 'username' in str(e):
                raise ValueError("Username already taken")
            else:
                raise ValueError("User already exists")
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            raise ValueError(f"Failed to create user: {str(e)}")
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address"""
        try:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow('''
                    SELECT id, email, username, hashed_password, first_name, last_name,
                           is_active, is_verified, created_at, updated_at, last_login
                    FROM users WHERE email = $1
                ''', email)
                
                return dict(user) if user else None
                
        except Exception as e:
            logger.error(f"❌ Failed to get user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID (without password hash)"""
        try:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow('''
                    SELECT id, email, username, first_name, last_name,
                           is_active, is_verified, created_at, updated_at, last_login
                    FROM users WHERE id = $1
                ''', user_id)
                
                return dict(user) if user else None
                
        except Exception as e:
            logger.error(f"❌ Failed to get user by ID: {e}")
            return None
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"❌ Password verification failed: {e}")
            return False
    
    async def update_user_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = $1
                ''', user_id)
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update user login: {e}")
            return False
    
    async def verify_user_email(self, verification_token: str) -> bool:
        """Verify user email with token"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute('''
                    UPDATE users 
                    SET is_verified = true, verification_token = NULL 
                    WHERE verification_token = $1 AND is_verified = false
                ''', verification_token)
                
                return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"❌ Failed to verify email: {e}")
            return False
    
    async def create_session(self, session_data: Dict) -> Optional[str]:
        """Create a new user session with refresh token"""
        try:
            async with self.pool.acquire() as conn:
                session_id = await conn.fetchval('''
                    INSERT INTO user_sessions (
                        user_id, refresh_token, device_info, ip_address, 
                        user_agent, expires_at
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                ''',
                    session_data['user_id'],
                    session_data['refresh_token'],
                    session_data.get('device_info'),
                    session_data.get('ip_address'),
                    session_data.get('user_agent'),
                    session_data['expires_at']
                )
                
                return session_data['refresh_token']
                
        except Exception as e:
            logger.error(f"❌ Failed to create session: {e}")
            return None
    
    async def get_session_by_token(self, refresh_token: str) -> Optional[Dict]:
        """Get session by refresh token"""
        try:
            async with self.pool.acquire() as conn:
                session = await conn.fetchrow('''
                    SELECT s.*, u.id as user_id, u.email, u.is_active 
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.refresh_token = $1 AND s.expires_at > CURRENT_TIMESTAMP
                ''', refresh_token)
                
                return dict(session) if session else None
                
        except Exception as e:
            logger.error(f"❌ Failed to get session: {e}")
            return None
    
    async def delete_session(self, refresh_token: str) -> bool:
        """Delete a session (logout)"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute('''
                    DELETE FROM user_sessions WHERE refresh_token = $1
                ''', refresh_token)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"❌ Failed to delete session: {e}")
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute('''
                    DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP
                ''')
                
                # Extract number from "DELETE n"
                deleted_count = int(result.split()[1]) if result.startswith("DELETE") else 0
                logger.info(f"🧹 Cleaned up {deleted_count} expired sessions")
                return deleted_count
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup sessions: {e}")
            return 0

# Global instance
auth_models = AuthModels()
