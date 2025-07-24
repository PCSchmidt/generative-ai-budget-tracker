#!/bin/bash

echo "� AI Budget Tracker Quick Start"
echo "================================"

# Check if we're in the right directory
if [[ ! -f "package.json" ]]; then
    echo "❌ Error: Please run this script from the generative-ai-budget-tracker directory"
    exit 1
fi

echo "� Setting up development environment..."

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "� Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file - please edit with your API keys"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "� Creating project directories..."
mkdir -p frontend/src/{components,screens,services,utils}
mkdir -p frontend/src/components/{charts,forms,insights,ui}
mkdir -p frontend/src/screens/{dashboard,expenses,insights,goals,settings}
mkdir -p backend/app/{api/endpoints,services,models,core}
mkdir -p backend/app/api/endpoints
mkdir -p ai/{prompts,models,training_data}
mkdir -p database/schemas

echo "✅ Directory structure created"

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose is available"
        echo ""
        echo "� Ready to start development with Docker!"
        echo "Run: docker-compose up --build"
    else
        echo "⚠️  Docker Compose not found - you may need to install it"
    fi
else
    echo "⚠️  Docker not found - please install Docker for development"
fi

echo ""
echo "�� Next Steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: docker-compose up --build"
echo "3. Open http://localhost:8000 for backend API"
echo "4. Open http://localhost:19006 for frontend"
echo ""
echo "� Full documentation available in .github/copilot-instructions.md"
echo "� This is app #2 of 10 in the AI apps roadmap!"
