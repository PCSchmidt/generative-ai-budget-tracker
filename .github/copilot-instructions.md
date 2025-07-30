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
- **Status**: ✅ **PHASE 1 COMPLETE** - Authentication & UI Foundation Ready
- **Difficulty**: Intermediate
- **Current Build**: Production-ready authentication system with password toggles
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

### Frontend (Web Application - COMPLETED PHASE 1)
- **Framework**: ✅ React 18.2.0 with React Router for web deployment
- **Authentication**: ✅ Professional login/signup forms with working password toggles
- **UI Components**: ✅ Modern fintech design system with professional styling
- **State Management**: ✅ Context API with complete authentication context
- **Navigation**: ✅ Protected routes and authentication flow
- **Development**: ✅ Hot reload development server at localhost:3000
- **Multi-Platform**: Web (✅ Complete), Mobile (🚧 Ready), Desktop (🚧 Ready)

### Backend & AI (INFRASTRUCTURE READY)
- **API Framework**: ✅ Python FastAPI with modern async architecture
- **Authentication**: ✅ JWT token models, bcrypt hashing, user management
- **Database Models**: ✅ User authentication, expense tracking ready
- **AI Services**: 🚧 Ready for Implementation
  - **Hugging Face**: Financial text analysis and categorization
  - **Groq**: Fast inference for real-time advice generation
  - **Custom Models**: Financial pattern recognition
- **Database**: ✅ PostgreSQL schema and models configured
- **Security**: ✅ CORS, input validation, secure headers implemented
- **Deployment**: ✅ Docker containerization ready for Railway/Vercel

### Development & Deployment (Docker-First)
- **Development Environment**: Docker Compose for all services
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Backend Hosting**: Railway or Vercel (proven from Journal Summarizer)
- **Mobile Testing**: Docker container with React Native
- **Database**: Docker PostgreSQL for development

## 🏗️ Project Architecture (Complete Infrastructure Ready)

### Directory Structure (CURRENT REALITY)
```
generative-ai-budget-tracker/
├── 🎯 FRONTEND (React Web App - PHASE 1 COMPLETE)
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/              # ✅ ProtectedRoute component
│   │   │   └── ui/                # ✅ Professional Button, Card, LoadingSpinner
│   │   ├── screens/
│   │   │   ├── auth/              # ✅ LoginScreen, SignupScreen with password toggles
│   │   │   ├── dashboard/         # ✅ DashboardScreen with welcome UI
│   │   │   └── LandingPage.js     # ✅ Professional landing page
│   │   ├── contexts/
│   │   │   └── AuthContext.js     # ✅ Complete authentication context
│   │   ├── services/
│   │   │   └── api.js             # ✅ API service with auth handling
│   │   ├── styles/
│   │   │   └── GlobalStyles.css   # ✅ Modern fintech design system
│   │   ├── theme/
│   │   │   └── index.js           # ✅ Professional color palette & typography
│   │   └── utils/                 # 🚧 Ready for implementation
│   ├── public/
│   │   ├── index.html             # ✅ Professional HTML with Inter font
│   │   └── manifest.json          # ✅ PWA configuration
│   ├── App.js                     # ✅ React Router with auth flows
│   ├── index.js                   # ✅ React 18 root rendering
│   └── package.json               # ✅ All dependencies locked
│
├── 🔧 BACKEND (Python FastAPI - INFRASTRUCTURE READY)
│   ├── app/
│   │   ├── auth/
│   │   │   ├── models.py          # ✅ User authentication models
│   │   │   └── mock_db.py         # ✅ Development database mock
│   │   ├── api/endpoints/         # 🚧 Ready for expense, budget endpoints
│   │   ├── services/              # 🚧 Ready for AI service implementation
│   │   └── core/                  # 🚧 Config, database, security setup
│   ├── Dockerfile                 # ✅ Production-ready FastAPI container
│   ├── start.sh                   # ✅ Backend initialization script
│   └── requirements.txt           # ✅ Python dependencies defined
│
├── 🐳 DOCKER INFRASTRUCTURE (READY)
│   ├── Dockerfile.web             # ✅ Web frontend containerization
│   ├── docker-compose.yml         # 🚧 Multi-service development setup
│   └── .env.example               # ✅ Environment variable template
│
├── 📚 DOCUMENTATION (UPDATED)
│   ├── .github/
│   │   └── copilot-instructions.md # ✅ Complete development guide
│   ├── README.md                  # 🚧 Needs updating
│   └── docs/                      # 🚧 Technical documentation
│
├── 🚀 DEPLOYMENT (CONFIGURED)
│   ├── .gitignore                 # ✅ Clean repository management
│   ├── railway.json               # ✅ Railway deployment ready
│   └── vercel.json                # ✅ Vercel frontend deployment
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

## 📋 Development Phases

### Phase 1: Authentication & Modern UI Foundation (Week 1) ✅ COMPLETE
- ✅ **Authentication System**: JWT-based signup/login with password reset
- ✅ **Professional Design System**: Modern fintech UI components and color palette  
- ✅ **Multi-Platform Setup**: React web application with responsive design
- ✅ **Backend Auth**: User models, JWT tokens, FastAPI backend structure
- ✅ **Docker development environment**: Containerized development workflow
- ✅ **Password Toggles**: Working Show/Hide functionality on login/signup forms
- ✅ **Protected Routes**: Authentication flow with route protection
- ✅ **Repository**: Clean git history with proper commits and documentation

### Phase 2: Core App Features (Week 2) 🚧 READY TO START
- 🔲 **Dashboard Enhancement**: Add expense overview widgets and charts
- 🔲 **Expense Management**: Create, edit, delete expenses with user association
- 🔲 **Category System**: Implement expense categorization UI
- 🔲 **Database Integration**: Connect backend to PostgreSQL for data persistence
- 🔲 **API Integration**: Connect frontend to backend authentication endpoints

### Phase 3: AI Integration & Advanced Features (Week 3)
- 🔲 **AI Categorization**: Expense categorization with Hugging Face models
- 🔲 **Spending Analysis**: Pattern recognition and insights generation
- 🔲 **Financial Advice**: Personalized recommendations using Groq
- 🔲 **Data Visualization**: Interactive charts with Chart.js/Victory
- 🔲 **Goal Tracking**: Financial goal setting and progress monitoring

### Phase 4: Production & Multi-Platform Deployment (Week 4)
- 🔲 **Production Deployment**: Deploy to Railway/Vercel with environment configs
- 🔲 **Performance Optimization**: Caching, lazy loading, API optimization
- 🔲 **Security Hardening**: Rate limiting, security headers, input validation
- 🔲 **Mobile Adaptation**: Progressive Web App features for mobile
- 🔲 **Portfolio Integration**: Professional demo with complete feature showcase

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
