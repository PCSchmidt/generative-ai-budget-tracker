# GitHub Copilot Instructions - AI Budget Tracker

## νΎ― Project Overview

This is the **second app** in the comprehensive roadmap for building **10 commercializable generative AI mobile apps**. The AI Budget Tracker is a smart money management application that uses AI to analyze spending patterns, provide personalized financial advice, and help users make better financial decisions.

### Key Objectives
- Build a production-ready AI-powered budget tracking mobile app
- Implement advanced AI features for financial analysis and insights
- Create a strong portfolio piece demonstrating financial AI capabilities
- Use Docker-first development approach (lesson learned from Journal Summarizer)
- Focus on real-world commercializable financial application

## ν³± App Specific Details

### **AI Budget Tracker - Smart Money Management**
- **Repository**: `generative-ai-budget-tracker`
- **Status**: Ready for Development (Infrastructure Complete)
- **Difficulty**: Intermediate
- **Primary AI Features**: 
  - Expense categorization and analysis
  - Spending pattern recognition
  - Personalized financial advice generation
  - Budget optimization recommendations
  - Financial goal tracking and predictions

**What it does**: Analyzes your spending patterns and provides personalized financial advice using AI.  
**Why people love it**: Goes beyond basic tracking to offer intelligent insights about spending habits and financial health.  
**What you'll learn**: Financial data analysis, predictive modeling, recommendation systems, data visualization  
**Perfect for**: Young professionals, students, anyone wanting better financial health

## ν» οΈ Technology Stack (Proven from Journal Summarizer)

### Development Approach
- **Container-First Development**: Use Docker for all development (lesson learned from Journal Summarizer Expo issues)
- **Backend-First Strategy**: Build and test API endpoints before frontend integration
- **AI Integration**: Start with Hugging Face models, add other providers as needed

### Frontend (Mobile App)
- **Framework**: React Native with Docker containerization
- **Navigation**: React Navigation v6
- **UI Components**: React Native Elements / NativeBase
- **State Management**: Redux Toolkit or Context API
- **Charts/Visualization**: Victory Native for financial charts
- **Development**: Docker container for consistent environment

### Backend & AI
- **API Framework**: Python FastAPI (proven reliable in Journal Summarizer)
- **AI Services**: 
  - **Hugging Face**: Financial text analysis and categorization
  - **Groq**: Fast inference for real-time advice generation
  - **Custom Models**: Financial pattern recognition
- **Database**: SQLite for development, PostgreSQL for production
- **Vector Database**: FAISS for financial knowledge base and recommendations

### Development & Deployment (Docker-First)
- **Development Environment**: Docker Compose for all services
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Backend Hosting**: Railway or Vercel (proven from Journal Summarizer)
- **Mobile Testing**: Docker container with React Native
- **Database**: Docker PostgreSQL for development

## νΏοΈ Project Architecture (Complete Infrastructure Ready)

### Directory Structure
```
generative-ai-budget-tracker/
βββ ν³± FRONTEND (React Native in Docker)
β   βββ src/
β   β   βββ components/
β   β   β   βββ charts/           # Financial visualization components
β   β   β   βββ forms/            # Expense entry forms
β   β   β   βββ insights/         # AI insight display components
β   β   β   βββ ui/               # Base UI components
β   β   βββ screens/
β   β   β   βββ dashboard/        # Main dashboard with spending overview
β   β   β   βββ expenses/         # Expense entry and management
β   β   β   βββ insights/         # AI-generated financial insights
β   β   β   βββ goals/            # Financial goal setting and tracking
β   β   β   βββ settings/         # App settings and preferences
β   β   βββ services/
β   β   β   βββ api.js            # API client for backend communication
β   β   β   βββ budgetService.js  # Budget calculation logic
β   β   β   βββ chartService.js   # Data formatting for charts
β   β   βββ utils/
β   β       βββ currencyUtils.js  # Currency formatting utilities
β   β       βββ dateUtils.js      # Date range calculations
β   β       βββ categoryUtils.js  # Expense category helpers
β   βββ Dockerfile                # React Native container
β   βββ package.json              # Dependencies and scripts
β
βββ ν΄ BACKEND (Python FastAPI in Docker)
β   βββ app/
β   β   βββ api/endpoints/
β   β   β   βββ expenses.py       # Expense CRUD operations
β   β   β   βββ budgets.py        # Budget management
β   β   β   βββ insights.py       # AI-generated insights
β   β   β   βββ goals.py          # Financial goal tracking
β   β   β   βββ analytics.py      # Spending analytics
β   β   βββ services/
β   β   β   βββ ai_service.py     # Main AI processing service
β   β   β   βββ expense_analyzer.py # Expense categorization AI
β   β   β   βββ insight_generator.py # Financial advice AI
β   β   β   βββ pattern_detector.py # Spending pattern analysis
β   β   β   βββ goal_predictor.py # Goal achievement predictions
β   β   βββ models/
β   β   β   βββ expense.py        # Expense data models
β   β   β   βββ budget.py         # Budget data models
β   β   β   βββ goal.py           # Financial goal models
β   β   β   βββ user.py           # User management models
β   β   βββ core/
β   β       βββ config.py         # App configuration
β   β       βββ database.py       # Database connection
β   β       βββ security.py       # Authentication
β   βββ Dockerfile                # FastAPI container
β   βββ requirements.txt          # Python dependencies
β   βββ main.py                   # FastAPI entry point
β
βββ ν·οΈ DATABASE (PostgreSQL in Docker)
β   βββ docker-compose.yml        # Complete development environment
β   βββ init.sql                  # Database initialization
β   βββ schemas/                  # Database schema definitions
β
βββ ν·  AI SPECIFIC
β   βββ prompts/
β   β   βββ expense_categorization.txt
β   β   βββ financial_advice.txt
β   β   βββ spending_analysis.txt
β   β   βββ goal_recommendations.txt
β   βββ models/                   # AI model configurations
β   βββ training_data/            # Sample financial data for testing
β
βββ νΊ DEPLOYMENT
β   βββ .github/workflows/
β   β   βββ deploy.yml            # Deployment automation
β   β   βββ test.yml              # Automated testing
β   βββ railway.json              # Railway deployment config
β   βββ vercel.json               # Vercel deployment config (backend)
β   βββ docker-compose.prod.yml   # Production container setup
```

## ν΄§ Development Workflow (Docker-First Approach)

### Getting Started
```bash
# 1. Clone the repository
git clone https://github.com/PCSchmidt/generative-ai-budget-tracker.git
cd generative-ai-budget-tracker

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start complete development environment with Docker
docker-compose up --build

# Frontend: http://localhost:19006
# Backend API: http://localhost:8000
# Database: PostgreSQL on port 5432
```

### Key Development Commands
```bash
# Start all services
docker-compose up

# Rebuild after changes
docker-compose up --build

# Run tests
docker-compose exec backend pytest
docker-compose exec frontend npm test

# Database operations
docker-compose exec db psql -U budget_user -d budget_tracker

# View logs
docker-compose logs backend
docker-compose logs frontend
```

## ν΄ AI Integration Strategy

### Primary AI Features to Implement

#### 1. **Expense Categorization AI**
```python
# Example implementation approach
class ExpenseCategorizer:
    def categorize_expense(self, description: str, amount: float) -> str:
        # Use Hugging Face model for text classification
        # Categories: Food, Transportation, Entertainment, Utilities, etc.
```

#### 2. **Spending Pattern Analysis**
```python
class SpendingPatternAnalyzer:
    def analyze_patterns(self, user_expenses: List[Expense]) -> Dict:
        # Identify spending trends, unusual expenses, recurring patterns
        # Generate insights about spending behavior
```

#### 3. **Financial Advice Generator**
```python
class FinancialAdvisor:
    def generate_advice(self, spending_data: Dict, goals: List[Goal]) -> str:
        # Use AI to generate personalized financial advice
        # Consider spending patterns, income, goals
```

#### 4. **Budget Optimization**
```python
class BudgetOptimizer:
    def optimize_budget(self, current_budget: Budget, historical_data: List) -> Budget:
        # AI-powered budget recommendations
        # Based on spending patterns and financial goals
```

### AI Models and APIs
- **Hugging Face**: Text classification for expense categorization
- **Groq**: Fast inference for real-time advice generation
- **Custom Prompts**: Financial domain-specific prompt engineering
- **Vector Database**: Store financial knowledge base for contextual advice

## ν²Ύ Important Configuration Files

### Environment Variables (.env)
```bash
# Essential for AI Budget Tracker
DEBUG=true
SECRET_KEY=your-budget-tracker-secret-key

# Database
DATABASE_URL=postgresql://budget_user:budget_pass@localhost:5432/budget_tracker

# AI Services
HUGGINGFACE_API_KEY=your-hf-key
GROQ_API_KEY=your-groq-key
OPENAI_API_KEY=your-openai-key (optional)

# Financial Data APIs (for real bank integration - advanced feature)
PLAID_CLIENT_ID=your-plaid-client-id (future feature)
PLAID_SECRET=your-plaid-secret (future feature)

# App Configuration
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:19006
```

### Docker Compose Configuration
```yaml
# Proven setup from Journal Summarizer experience
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://budget_user:budget_pass@db:5432/budget_tracker
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "19006:19006"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: budget_tracker
      POSTGRES_USER: budget_user
      POSTGRES_PASSWORD: budget_pass
    ports:
      - "5432:5432"
    volumes:
      - budget_data:/var/lib/postgresql/data
```

## νΎ― Development Phases

### Phase 1: Core Infrastructure (Week 1)
- β Set up Docker development environment
- β Create database schema for expenses, budgets, goals
- β Build basic CRUD API endpoints
- β Create expense entry forms
- β Basic expense listing and viewing

### Phase 2: AI Integration (Week 2)
- ν΄¨ Implement expense categorization AI
- ν΄¨ Add spending pattern analysis
- ν΄¨ Create financial insight generation
- ν΄¨ Build AI-powered budget recommendations

### Phase 3: Advanced Features (Week 3)
- ν³ Financial goal tracking and predictions
- ν³ Advanced data visualization with charts
- ν³ Export functionality (PDF reports)
- ν³ Spending alerts and notifications

### Phase 4: Production Deployment (Week 4)
- ν³ Deploy backend to Railway/Vercel
- ν³ Set up production database
- ν³ Mobile app building and distribution
- ν³ Performance optimization and monitoring

## ν΄ Key Dependencies

### Backend Dependencies
```txt
# Core FastAPI setup
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# AI and ML
transformers==4.36.0
torch==2.1.0
huggingface-hub==0.19.4
groq==0.4.1

# Financial calculations
pandas==2.1.4
numpy==1.25.2
scikit-learn==1.3.2

# Database and Auth
alembic==1.13.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "react-native": "0.72.6",
    "expo": "~49.0.0",
    "@react-navigation/native": "^6.1.0",
    "victory-native": "^36.6.8",
    "react-native-elements": "^3.4.3",
    "axios": "^1.6.0",
    "react-native-paper": "^5.10.0"
  }
}
```

## νΊ¨ Common Issues and Solutions (From Journal Summarizer Experience)

### Docker Development Issues
- **Port Conflicts**: Change ports in docker-compose.yml if needed
- **Container Rebuild**: Run `docker-compose down && docker-compose up --build` after major changes
- **Database Connection**: Ensure database container is healthy before backend starts

### AI Integration Issues
- **Model Loading**: Start with smaller models, upgrade to larger ones after basic functionality works
- **API Rate Limits**: Implement fallback responses for when AI APIs are unavailable
- **Slow Response Times**: Use Groq for fast inference, cache common responses

### Deployment Issues
- **Environment Variables**: Double-check all required environment variables are set
- **Database Migrations**: Run migrations before starting the app in production
- **Container Size**: Optimize Docker images for faster deployment

## νΎ― Success Metrics

### Technical Goals
- β Complete expense entry and categorization system
- β AI-powered spending analysis with >80% accuracy
- β Real-time financial insights and recommendations
- β Responsive mobile interface with charts and visualizations
- β Production deployment with monitoring

### Portfolio Impact
- Demonstrates financial AI expertise
- Shows advanced data visualization skills
- Proves ability to handle sensitive financial data securely
- Creates marketable fintech application

## ν΄ Development Best Practices

### Code Standards
- **API Design**: RESTful endpoints with proper HTTP status codes
- **Database**: Proper indexing for financial queries, data validation
- **Security**: Encrypt sensitive financial data, implement proper authentication
- **Testing**: Unit tests for financial calculations, integration tests for AI features
- **Documentation**: Clear API documentation, financial calculation explanations

### AI Development
- **Prompt Engineering**: Test prompts thoroughly with various financial scenarios
- **Model Selection**: Start with proven models, avoid over-engineering
- **Error Handling**: Graceful fallbacks when AI services are unavailable
- **Performance**: Cache common AI responses, optimize for mobile usage

## ν²‘ Advanced Features (Future Enhancements)

### Bank Integration
- Plaid API integration for automatic transaction import
- Real-time bank account monitoring
- Automatic expense categorization from bank data

### Machine Learning
- Personal spending prediction models
- Custom categorization based on user behavior
- Anomaly detection for unusual spending

### Social Features
- Family budget sharing and collaboration
- Spending challenges and goals with friends
- Community-driven financial tips and advice

## ν΄ Key Resources

### Documentation Links
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Native Docs**: https://reactnative.dev/docs/getting-started
- **Hugging Face Models**: https://huggingface.co/models
- **Victory Charts**: https://formidable.com/open-source/victory/

### API References
- **Hugging Face Inference API**: For expense categorization
- **Groq API**: For fast financial advice generation
- **Plaid API**: For bank integration (advanced feature)

### Design Inspiration
- **Mint**: Expense categorization and insights
- **YNAB**: Budget allocation and goal tracking
- **Personal Capital**: Financial analysis and recommendations

---

## νΊ Quick Start Commands

```bash
# Complete setup (run from project root)
cp .env.example .env
docker-compose up --build

# Development workflow
docker-compose exec backend pytest  # Run backend tests
docker-compose exec frontend npm test  # Run frontend tests
docker-compose logs -f backend  # Monitor backend logs

# Database operations
docker-compose exec db psql -U budget_user -d budget_tracker
```

**Remember**: This is a Docker-first development approach based on successful experience with the Journal Summarizer. Start with the backend API, test thoroughly, then build the frontend integration.

---

*This document contains all the context and guidance needed for successful AI Budget Tracker development. Reference this file throughout the development process for consistent decision-making and technical approach.*
