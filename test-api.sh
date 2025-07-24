#!/bin/bash
# Test script for AI Budget Tracker API on Railway

echo "🚀 Testing AI Budget Tracker API..."
echo "=================================="

# Get Railway status and URL
echo "📡 Getting Railway deployment info..."
railway status

echo ""
echo "🔍 Testing API endpoints..."

# Test root endpoint
echo "Testing root endpoint (/)..."
curl -s https://your-app-url.railway.app/ | jq .

echo ""
echo "Testing health endpoint (/health)..."
curl -s https://your-app-url.railway.app/health | jq .

echo ""
echo "Testing expenses endpoint (/api/expenses)..."
curl -s https://your-app-url.railway.app/api/expenses | jq .

echo ""
echo "Testing insights endpoint (/api/insights)..."
curl -s https://your-app-url.railway.app/api/insights | jq .

echo ""
echo "✅ API testing complete!"
