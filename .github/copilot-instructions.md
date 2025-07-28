# GitHub Copilot Instructions - AI Budget Tracker

## ��� Project Overview

This is the **second app** in the comprehensive roadmap for building **10 commercializable generative AI mobile apps**. The AI Budget Tracker is a smart money management application that uses AI to analyze spending patterns, provide personalized financial advice, and help users make better financial decisions.

### Key Objectives
- Build a production-ready AI-powered budget tracking mobile app
- Implement advanced AI features for financial analysis and insights
- Create a strong portfolio piece demonstrating financial AI capabilities
- Use Docker-first development approach (lesson learned from Journal Summarizer)
- Focus on real-world commercializable financial application
- **🔐 PRIORITY: Implement modern authentication system with signup/login**
- **🎨 PRIORITY: Create sophisticated, professional UI/UX design**
- **📱 PRIORITY: Support multi-platform deployment (web, mobile, desktop)**

## ��� App Specific Details

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

## ���️ Technology Stack (Proven from Journal Summarizer)

### Development Approach
- **Container-First Development**: Use Docker for all development (lesson learned from Journal Summarizer Expo issues)
- **Backend-First Strategy**: Build and test API endpoints before frontend integration
- **AI Integration**: Start with Hugging Face models, add other providers as needed

### Frontend (Mobile App)
- **Framework**: React Native with Docker containerization
- **Navigation**: React Navigation v6 with authentication flows
- **UI Components**: Custom design system with professional fintech aesthetics
- **Authentication**: JWT-based auth with signup/login/password reset
- **State Management**: Context API with authentication context
- **Charts/Visualization**: Chart.js and Victory Native for financial charts
- **Development**: Docker container for consistent environment
- **Multi-Platform**: Web (React), Mobile (React Native), Desktop (Electron)

### Backend & AI
- **API Framework**: Python FastAPI (proven reliable in Journal Summarizer)
- **Authentication**: JWT tokens, bcrypt password hashing, email verification
- **AI Services**: 
  - **Hugging Face**: Financial text analysis and categorization
  - **Groq**: Fast inference for real-time advice generation
  - **Custom Models**: Financial pattern recognition
- **Database**: PostgreSQL with user management and expense tracking
- **Vector Database**: FAISS for financial knowledge base and recommendations
- **Security**: Rate limiting, CORS, input validation, secure headers

### Development & Deployment (Docker-First)
- **Development Environment**: Docker Compose for all services
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Backend Hosting**: Railway or Vercel (proven from Journal Summarizer)
- **Mobile Testing**: Docker container with React Native
- **Database**: Docker PostgreSQL for development

## ���️ Project Architecture (Complete Infrastructure Ready)

### Directory Structure
```
generative-ai-budget-tracker/
├── ��� FRONTEND (React Native in Docker)
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/           # Financial visualization components
│   │   │   ├── forms/            # Expense entry forms
│   │   │   ├── insights/         # AI insight display components
│   │   │   └── ui/               # Base UI components
│   │   ├── screens/
│   │   │   ├── dashboard/        # Main dashboard with spending overview
│   │   │   ├── expenses/         # Expense entry and management
│   │   │   ├── insights/         # AI-generated financial insights
│   │   │   ├── goals/            # Financial goal setting and tracking
│   │   │   └── settings/         # App settings and preferences
│   │   ├── services/
│   │   │   ├── api.js            # API client for backend communication
│   │   │   ├── budgetService.js  # Budget calculation logic
│   │   │   └── chartService.js   # Data formatting for charts
│   │   └── utils/
│   │       ├── currencyUtils.js  # Currency formatting utilities
│   │       ├── dateUtils.js      # Date range calculations
│   │       └── categoryUtils.js  # Expense category helpers
│   ├── Dockerfile                # React Native container
│   └── package.json              # Dependencies and scripts
│
├── ��� BACKEND (Python FastAPI in Docker)
│   ├── app/
│   │   ├── api/endpoints/
│   │   │   ├── expenses.py       # Expense CRUD operations
│   │   │   ├── budgets.py        # Budget management
│   │   │   ├── insights.py       # AI-generated insights
│   │   │   ├── goals.py          # Financial goal tracking
│   │   │   └── analytics.py      # Spending analytics
│   │   ├── services/
│   │   │   ├── ai_service.py     # Main AI processing service
│   │   │   ├── expense_analyzer.py # Expense categorization AI
│   │   │   ├── insight_generator.py # Financial advice AI
│   │   │   ├── pattern_detector.py # Spending pattern analysis
│   │   │   └── goal_predictor.py # Goal achievement predictions
│   │   ├── models/
│   │   │   ├── expense.py        # Expense data models
│   │   │   ├── budget.py         # Budget data models
│   │   │   ├── goal.py           # Financial goal models
│   │   │   └── user.py           # User management models
│   │   └── core/
│   │       ├── config.py         # App configuration
│   │       ├── database.py       # Database connection
│   │       └── security.py       # Authentication
│   ├── Dockerfile                # FastAPI container
│   ├── requirements.txt          # Python dependencies
│   └── main.py                   # FastAPI entry point
│
├── ���️ DATABASE (PostgreSQL in Docker)
│   ├── docker-compose.yml        # Complete development environment
│   ├── init.sql                  # Database initialization
│   └── schemas/                  # Database schema definitions
│
├── ��� AI SPECIFIC
│   ├── prompts/
│   │   ├── expense_categorization.txt
│   │   ├── financial_advice.txt
│   │   ├── spending_analysis.txt
│   │   └── goal_recommendations.txt
│   ├── models/                   # AI model configurations
│   └── training_data/            # Sample financial data for testing
│
├── ��� DEPLOYMENT
│   ├── .github/workflows/
│   │   ├── deploy.yml            # Deployment automation
│   │   └── test.yml              # Automated testing
│   ├── railway.json              # Railway deployment config
│   ├── vercel.json               # Vercel deployment config (backend)
│   └── docker-compose.prod.yml   # Production container setup
```

## ��� Development Workflow (Docker-First Approach)

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

## ��� AI Integration Strategy

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

## ��� Important Configuration Files

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

# Authentication & Security
JWT_SECRET_KEY=your-super-secure-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Services (for verification and password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@your-domain.com
```

## ��� Authentication & Security Architecture

### User Authentication System
```python
# JWT-based authentication with secure practices
# Features:
# - Email verification on signup
# - Password reset via email
# - Refresh token rotation
# - Rate limiting on auth endpoints
# - Secure password hashing with bcrypt

# Database Schema:
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# User-specific expense tracking:
ALTER TABLE expenses ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE budgets ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE goals ADD COLUMN user_id INTEGER REFERENCES users(id);
```

### Professional UI/UX Design System
```css
/* Modern Fintech Color Palette */
:root {
  /* Primary Brand Colors */
  --primary-900: #0f172a;      /* Dark slate - headers, text */
  --primary-800: #1e293b;      /* Slate gray - navigation */
  --primary-700: #334155;      /* Medium slate - secondary text */
  --primary-600: #475569;      /* Light slate - borders */
  
  /* Accent Colors */
  --accent-600: #2563eb;       /* Professional blue - CTAs */
  --accent-500: #3b82f6;       /* Bright blue - links */
  --accent-400: #60a5fa;       /* Light blue - hover states */
  
  /* Financial Status Colors */
  --success-600: #059669;      /* Emerald - positive amounts */
  --error-600: #dc2626;        /* Red - negative amounts */
  --warning-600: #d97706;      /* Amber - alerts */
  
  /* Neutral Grays */
  --gray-50: #f8fafc;         /* Very light - backgrounds */
  --gray-100: #f1f5f9;        /* Light background */
  --gray-200: #e2e8f0;        /* Subtle borders */
  --gray-900: #0f172a;        /* Dark text */
}

/* Typography System */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Component Design Tokens */
--spacing-xs: 4px;    --border-radius-sm: 6px;
--spacing-sm: 8px;    --border-radius-md: 8px;
--spacing-md: 16px;   --border-radius-lg: 12px;
--spacing-lg: 24px;   --border-radius-xl: 16px;
--spacing-xl: 32px;   --border-radius-2xl: 24px;
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

## ��� Development Phases

### Phase 1: Authentication & Modern UI Foundation (Week 1)
- 🔐 **Authentication System**: JWT-based signup/login with password reset
- 🎨 **Professional Design System**: Modern fintech UI components and color palette
- 📱 **Multi-Platform Setup**: React Native with web/mobile/desktop support
- 🔧 **Backend Auth**: User models, JWT tokens, email verification
- ✅ Docker development environment (complete)

### Phase 2: Core App Features (Week 2)
- ��� **Protected Routes**: Authentication-gated expense management
- ��� **Dashboard Screens**: Professional financial overview with modern UI
- ��� **Expense Management**: Create, edit, delete expenses with user association
- ��� **Navigation System**: Bottom tabs with authentication flow
- ��� **Database Integration**: User-specific data persistence

### Phase 3: AI Integration & Advanced Features (Week 3)
- ��� **AI Categorization**: Expense categorization with user-specific learning
- ��� **Spending Analysis**: Pattern recognition and insights generation
- ��� **Financial Advice**: Personalized recommendations based on user data
- ��� **Data Visualization**: Interactive charts with Chart.js/Victory Native
- ��� **Goal Tracking**: Financial goal setting and progress monitoring

### Phase 4: Production & Multi-Platform Deployment (Week 4)
- ��� **Authentication Security**: Rate limiting, security headers, validation
- ��� **Multi-Platform Builds**: Web (Vercel), Mobile (Expo EAS), Desktop (Electron)
- ��� **Production Database**: Secure PostgreSQL with user management
- ��� **Performance Optimization**: Caching, lazy loading, API optimization
- ��� **Portfolio Integration**: Professional demo with authentication showcase

## ��� Key Dependencies

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

## ��� Common Issues and Solutions (From Journal Summarizer Experience)

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

## ��� Success Metrics

### Technical Goals
- ✅ Complete expense entry and categorization system
- ✅ AI-powered spending analysis with >80% accuracy
- ✅ Real-time financial insights and recommendations
- ✅ Responsive mobile interface with charts and visualizations
- ✅ Production deployment with monitoring

### Portfolio Impact
- Demonstrates financial AI expertise
- Shows advanced data visualization skills
- Proves ability to handle sensitive financial data securely
- Creates marketable fintech application

## ��� Development Best Practices

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

## ��� Advanced Features (Future Enhancements)

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

## ��� Key Resources

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

## ��� Quick Start Commands

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
