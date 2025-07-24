#!/bin/bash

echo "🚀 AI Budget Tracker - Local Development Setup"
echo "============================================="

# Check if we're in the right directory
if [[ ! -f "package.json" ]]; then
    echo "❌ Error: Please run this script from the generative-ai-budget-tracker directory"
    exit 1
fi

echo "📦 Starting with local development setup..."

# Option 1: Start just the database with Docker
echo ""
echo "🗄️ Starting PostgreSQL database only..."
docker-compose up db -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if database is running
if docker ps | grep -q budget_tracker_db; then
    echo "✅ Database is running on localhost:5432"
    echo ""
    echo "🔗 Database connection details:"
    echo "   Host: localhost"
    echo "   Port: 5432"
    echo "   Database: budget_tracker"
    echo "   Username: budget_user"
    echo "   Password: budget_pass"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Set up Python virtual environment in backend/"
    echo "2. Install dependencies: pip install -r backend/requirements.txt"
    echo "3. Start FastAPI: cd backend && uvicorn app.main:app --reload"
    echo "4. Set up React Native: cd frontend && npm install && npm start"
else
    echo "❌ Database failed to start"
    echo "Try: docker-compose logs db"
fi
