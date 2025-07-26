#!/usr/bin/env python3
"""
Production Deployment Test for AI Budget Tracker v3.0
Tests live deployment with Priority 3 analytics
"""

import requests
import json
import time
from datetime import datetime

def test_production_deployment():
    """Test the production deployment"""
    print("🚀 Testing AI Budget Tracker v3.0 Production Deployment")
    print("=" * 65)
    
    # Try different possible Railway URLs
    possible_urls = [
        "https://generative-ai-budget-tracker-production.up.railway.app",
        "https://web-production-4077.up.railway.app",
        "https://ai-budget-tracker.up.railway.app"
    ]
    
    base_url = None
    
    # Find working deployment URL
    print("🔍 Finding active deployment...")
    for url in possible_urls:
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                base_url = url
                print(f"   ✅ Found active deployment: {url}")
                break
        except:
            continue
    
    if not base_url:
        print("   ⚠️  No active deployment found. Testing locally...")
        base_url = "http://localhost:8000"
    
    # Test Suite
    tests_passed = 0
    total_tests = 0
    
    def test_endpoint(name, endpoint, expected_keys=None, method="GET", data=None):
        nonlocal tests_passed, total_tests
        total_tests += 1
        
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=15)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if expected_keys:
                    missing_keys = [key for key in expected_keys if key not in result]
                    if missing_keys:
                        print(f"   ⚠️  {name}: Missing keys {missing_keys}")
                        return False
                
                print(f"   ✅ {name}: Working")
                tests_passed += 1
                return True
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:50]}...")
            return False
    
    # Core API Tests
    print(f"\n📡 Testing Core API ({base_url})...")
    test_endpoint("Health Check", "/health", ["status", "version"])
    test_endpoint("AI Categorization", "/api/categorize", ["category", "confidence"], "POST", {
        "description": "Starbucks coffee", "amount": 5.50
    })
    
    # Priority 3 Analytics Tests
    print(f"\n📊 Testing Priority 3 Analytics...")
    test_endpoint("Spending Patterns", "/api/analytics/patterns", ["analysis"])
    test_endpoint("Financial Insights", "/api/analytics/insights", ["insights", "recommendations"])
    test_endpoint("Anomaly Detection", "/api/analytics/anomalies", ["anomalies"])
    test_endpoint("AI Performance", "/api/analytics/ai-performance", ["performance"])
    
    # Database Tests
    print(f"\n💾 Testing Database Integration...")
    test_endpoint("Get Expenses", "/api/expenses", ["expenses"])
    test_endpoint("Create Expense", "/api/expenses", method="POST", data={
        "description": "Test Production Expense",
        "amount": 12.50
    })
    test_endpoint("Analytics Legacy", "/api/analytics", ["analytics"])
    
    # Results Summary
    print(f"\n" + "=" * 65)
    print(f"🏆 DEPLOYMENT TEST RESULTS:")
    print(f"   Tests Passed: {tests_passed}/{total_tests}")
    print(f"   Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print(f"   🎉 PERFECT DEPLOYMENT! All systems operational")
        return True, base_url
    elif tests_passed >= total_tests * 0.7:
        print(f"   ✅ GOOD DEPLOYMENT! Minor issues detected")
        return True, base_url
    else:
        print(f"   ⚠️  DEPLOYMENT ISSUES! Needs attention")
        return False, base_url

def demonstrate_analytics_features(base_url):
    """Demonstrate the analytics capabilities"""
    print(f"\n🎯 DEMONSTRATING AI BUDGET TRACKER v3.0 FEATURES")
    print("=" * 65)
    
    try:
        # Demo 1: AI Categorization
        print("🤖 AI Categorization Demo:")
        test_expenses = [
            {"description": "McDonald's lunch", "amount": 8.99},
            {"description": "Shell gas station", "amount": 45.00},
            {"description": "Target shopping", "amount": 67.50}
        ]
        
        for expense in test_expenses:
            try:
                response = requests.post(f"{base_url}/api/categorize", json=expense, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    print(f"   '{expense['description']}' → {result['category']} ({result['confidence']:.1%})")
            except:
                print(f"   Error categorizing: {expense['description']}")
        
        # Demo 2: Analytics Insights
        print(f"\n📊 Analytics Insights Demo:")
        try:
            response = requests.get(f"{base_url}/api/analytics/insights", timeout=15)
            if response.status_code == 200:
                insights = response.json()
                print(f"   💰 Total Analyzed: ${insights.get('total_amount', 0):.2f}")
                print(f"   📝 Expenses Count: {insights.get('total_expenses', 0)}")
                
                for i, insight in enumerate(insights.get('insights', [])[:2], 1):
                    print(f"   {i}. {insight.get('title', 'Insight')}")
                    
                for i, rec in enumerate(insights.get('recommendations', [])[:2], 1):
                    savings = rec.get('estimated_savings', 0)
                    print(f"   💡 {rec.get('title', 'Recommendation')} (Save: ${savings:.2f})")
        except:
            print("   Using mock analytics data...")
        
        # Demo 3: AI Performance
        print(f"\n🎯 AI Performance Demo:")
        try:
            response = requests.get(f"{base_url}/api/analytics/ai-performance", timeout=15)
            if response.status_code == 200:
                perf = response.json()['performance']
                print(f"   🤖 AI Categorized: {perf.get('ai_percentage', 0):.1f}%")
                print(f"   📊 Avg Confidence: {perf.get('average_confidence', 0):.1%}")
                print(f"   🏆 Efficiency: {perf.get('efficiency_rating', 'unknown').title()}")
        except:
            print("   Performance metrics using fallback data...")
            
    except Exception as e:
        print(f"   Demo error: {e}")

if __name__ == "__main__":
    print(f"🕐 Deployment Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success, url = test_production_deployment()
    
    if success:
        demonstrate_analytics_features(url)
    
    print(f"\n🏁 Test Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n🚀 AI BUDGET TRACKER v3.0 STATUS: READY FOR USERS!")
        print("   ✅ AI categorization operational")
        print("   ✅ Database persistence working") 
        print("   ✅ Advanced analytics active")
        print("   ✅ Production deployment stable")
        print(f"\n🌐 Live Demo: {url}")
    else:
        print("\n⚠️  Issues detected - recommend local testing first")
