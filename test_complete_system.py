#!/usr/bin/env python3
"""
Complete System Test for AI Budget Tracker
Tests AI categorization + Database integration end-to-end
"""

import sys
import os
import asyncio
import json
from datetime import date

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_complete_system():
    """Test the complete AI + Database pipeline"""
    print("🧪 Testing AI Budget Tracker Complete System")
    print("=" * 50)
    
    try:
        # Import our modules
        from backend.app.ai_categorizer import expense_categorizer
        from backend.app.expense_db import expense_db
        
        print("✅ Modules imported successfully")
        
        # Test 1: AI Categorization
        print("\n🤖 Testing AI Categorization...")
        test_expense = "Starbucks coffee $5.50"
        category_result = await expense_categorizer.categorize_expense(test_expense, 5.50)
        print(f"   Input: {test_expense}")
        print(f"   AI Result: {category_result}")
        
        # Test 2: Database Connection (without DATABASE_URL it should fallback gracefully)
        print("\n💾 Testing Database Connection...")
        db_initialized = await expense_db.init_pool()
        print(f"   Database initialized: {db_initialized}")
        
        # Test 3: Create expense with AI data
        print("\n📝 Testing Expense Creation...")
        expense_data = {
            'description': test_expense,
            'amount': 5.50,
            'category': category_result['category'],
            'category_confidence': category_result['confidence'],
            'categorization_method': category_result['method'],
            'ai_data': category_result,
            'expense_date': date.today()
        }
        
        if db_initialized:
            created_expense = await expense_db.create_expense(expense_data)
            print(f"   Created expense: {created_expense}")
            
            # Test 4: Retrieve expenses
            print("\n📊 Testing Expense Retrieval...")
            expenses = await expense_db.get_expenses()
            print(f"   Found {len(expenses)} expenses")
            
            # Test 5: Analytics
            print("\n📈 Testing Analytics...")
            analytics = await expense_db.get_spending_analytics()
            print(f"   Analytics: {analytics}")
            
        else:
            print("   ⚠️  Database not available, testing AI categorization only")
            print(f"   Would create: {expense_data}")
        
        print("\n🎉 System Test Complete!")
        print("✅ AI categorization working")
        print(f"{'✅' if db_initialized else '⚠️ '} Database {'working' if db_initialized else 'fallback mode'}")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set environment for testing
    os.environ.setdefault('HUGGINGFACE_API_KEY', 'test')
    
    result = asyncio.run(test_complete_system())
    sys.exit(0 if result else 1)
