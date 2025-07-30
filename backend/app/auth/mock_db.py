"""
Mock database adapter for testing authentication without PostgreSQL
This allows us to test the authentication flow locally without Docker/PostgreSQL
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class MockAuthDB:
    """In-memory database for testing authentication"""
    
    def __init__(self):
        self.users = {}  # Store users by email
        self.sessions = {}  # Store sessions by token
        self.user_counter = 1
        
        # Initialize with test user that was created during signup
        self._initialize_test_user()
    
    def _initialize_test_user(self):
        """Initialize with test user for login testing"""
        test_email = "test@example.com"
        test_password = "TestPassword123!"
        
        # Hash password
        hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        
        # Create test user
        user = {
            'id': 1,
            'email': test_email,
            'username': 'testuser',
            'hashed_password': hashed_password.decode('utf-8'),
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'is_verified': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login': None
        }
        
        self.users[test_email] = user
        self.user_counter = 2
        print(f"🔧 Mock database initialized with test user: {test_email}")
        
    async def create_auth_tables(self):
        """Mock table creation - just initialize storage"""
        print("✅ Mock authentication tables initialized")
        return True
        
    async def create_user(self, email: str, username: str, password: str, 
                         first_name: str = None, last_name: str = None) -> Dict:
        """Create a new user account"""
        
        # Check if user already exists
        if email in self.users:
            raise ValueError("User with this email already exists")
            
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user record
        user_id = self.user_counter
        self.user_counter += 1
        
        user = {
            'id': user_id,
            'email': email,
            'username': username,
            'hashed_password': hashed_password.decode('utf-8'),
            'first_name': first_name,
            'last_name': last_name,
            'is_active': True,
            'is_verified': True,  # Auto-verify for testing
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        self.users[email] = user
        print(f"✅ Mock user created: {email} (ID: {user_id})")
        
        # Return full user data (excluding hashed_password for response)
        return {
            'id': user_id,
            'email': email,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'is_active': True,
            'is_verified': True,
            'created_at': user['created_at'],
            'updated_at': user['updated_at']
        }
        
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user with email and password"""
        
        if email not in self.users:
            return None
            
        user = self.users[email]
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
            return {
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'is_active': user['is_active']
            }
        
        return None
        
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        if email in self.users:
            user = self.users[email]
            return {
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'hashed_password': user['hashed_password'],  # Include for authentication
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'is_active': user['is_active'],
                'is_verified': user['is_verified'],
                'created_at': user['created_at'],
                'updated_at': user['updated_at']
            }
        return None
        
    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        for user in self.users.values():
            if user['id'] == user_id:
                return {
                    'id': user['id'],
                    'email': user['email'],
                    'username': user['username'],
                    'hashed_password': user['hashed_password'],  # Include for authentication
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'is_active': user['is_active'],
                    'is_verified': user['is_verified'],
                    'created_at': user['created_at'],
                    'updated_at': user['updated_at']
                }
        return None
        
    async def update_user_login(self, user_id: int) -> bool:
        """Update user's last login time"""
        for user in self.users.values():
            if user['id'] == user_id:
                user['last_login'] = datetime.utcnow()
                user['updated_at'] = datetime.utcnow()
                print(f"✅ Updated last login for user {user_id}")
                return True
        return False
        
    async def create_user_session(self, user_id: int, refresh_token: str, 
                                 device_info: str = None, ip_address: str = None) -> bool:
        """Create a user session"""
        session = {
            'user_id': user_id,
            'refresh_token': refresh_token,
            'device_info': device_info,
            'ip_address': ip_address,
            'expires_at': datetime.utcnow() + timedelta(days=7),
            'created_at': datetime.utcnow()
        }
        
        self.sessions[refresh_token] = session
        print(f"✅ Mock session created for user {user_id}")
        return True
        
    async def get_session(self, refresh_token: str) -> Optional[Dict]:
        """Get session by refresh token"""
        if refresh_token in self.sessions:
            session = self.sessions[refresh_token]
            if session['expires_at'] > datetime.utcnow():
                return session
        return None
        
    async def delete_session(self, refresh_token: str) -> bool:
        """Delete a session"""
        if refresh_token in self.sessions:
            del self.sessions[refresh_token]
            print(f"✅ Mock session deleted")
            return True
        return False
        
    async def close(self):
        """Close database connection (mock)"""
        print("✅ Mock database connection closed")

# Global instance for testing
mock_auth_db = MockAuthDB()
