#!/bin/bash

echo "🧪 AI Budget Tracker - Environment Test"
echo "====================================="

# Test Docker installation
echo "🐳 Testing Docker installation..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed: $(docker --version)"
else
    echo "❌ Docker is not installed"
    exit 1
fi

# Test Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose is available: $(docker-compose --version)"
else
    echo "❌ Docker Compose is not available"
    exit 1
fi

# Check if .env exists
echo ""
echo "⚙️  Testing environment configuration..."
if [[ -f ".env" ]]; then
    echo "✅ .env file exists"
else
    echo "⚠️  .env file not found - creating from template..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "📝 Please edit .env file with your API keys before running docker-compose"
fi

# Test directory structure
echo ""
echo "📁 Testing directory structure..."
required_dirs=("backend" "frontend" "database" "ai")
for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "✅ $dir/ directory exists"
    else
        echo "❌ $dir/ directory missing"
    fi
done

# Test key files
echo ""
echo "📄 Testing key configuration files..."
key_files=("docker-compose.yml" "backend/requirements.txt" "backend/Dockerfile" "frontend/package.json" "frontend/Dockerfile" "database/init.sql")
for file in "${key_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

echo ""
echo "🚀 Test Results Summary:"
echo "======================="

# Count the checks
total_checks=0
passed_checks=0

# Docker checks
if command -v docker &> /dev/null; then
    ((passed_checks++))
fi
((total_checks++))

if command -v docker-compose &> /dev/null; then
    ((passed_checks++))
fi
((total_checks++))

# Directory checks
for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        ((passed_checks++))
    fi
    ((total_checks++))
done

# File checks
for file in "${key_files[@]}"; do
    if [[ -f "$file" ]]; then
        ((passed_checks++))
    fi
    ((total_checks++))
done

echo "✅ Passed: $passed_checks/$total_checks checks"

if [[ $passed_checks -eq $total_checks ]]; then
    echo ""
    echo "🎉 All tests passed! Your environment is ready for development."
    echo ""
    echo "🚀 Next steps:"
    echo "1. Edit .env file with your API keys"
    echo "2. Run: docker-compose up --build"
    echo "3. Open http://localhost:8000/docs for backend API"
    echo "4. Open http://localhost:19006 for frontend"
    echo ""
    echo "📚 See DEVELOPMENT_STATUS.md for detailed next steps"
else
    echo ""
    echo "⚠️  Some checks failed. Please review the missing components above."
    echo "📚 Refer to the setup documentation for help."
fi
