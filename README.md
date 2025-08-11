# 🤖 AI Budget Tracker - Smart Money Management

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/PCSchmidt/generative-ai-budget-tracker.svg)](https://github.com/PCSchmidt/generative-ai-budget-tracker/stargazers)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Ready-green.svg)](https://fastapi.tiangolo.com/)

> **Part of the [10 Commercializable AI Apps Roadmap](https://github.com/PCSchmidt/roadmap-for-building-generative-ai-apps)** - A comprehensive learning journey building production-ready AI-powered applications.

## 📖 Overview

The AI Budget Tracker is a modern smart money management application that uses artificial intelligence to analyze spending patterns, provide personalized financial advice, and help users make better financial decisions. 

**🎯 Current Status: Phase 3 (Backend Core + Financial Domain Implemented)**
- ✅ **Authentication & Security** (Phase 1)
- ✅ **Expense Management CRUD + Categorization Base**
- ✅ **Budgets & Goals Domain (auto budget spent sync)**
- ✅ **AI Endpoints (categorization, advice, insights) + Caching**
- ✅ **Robust Test Infrastructure (43 passing, transactional isolation)**
- 🚧 **Frontend Budget & Goal Visualization UI**
- 🚧 **Enhanced AI Model Integration (Groq / Hugging Face live models)**

---

## ✨ Key Features

### 🔐 Authentication System ✅
Modern JWT auth (access + rotating refresh), password policy, protected routes.

### 💰 Expense Management ✅
Create / update / delete expenses; categorized & used for analytics.

### 📏 Budgets (NEW) ✅
- Per-user monthly (period like YYYY-MM) budget objects: `total_limit`, `spent_amount` (auto)
- Automatic `spent_amount` recalculation on expense create/update/delete or period change
- Utilization & remaining values returned in responses
- Uniqueness enforced per (user, period)

### 🎯 Financial Goals (NEW) ✅
- Track savings goals with `target_amount` & `current_amount`
- Contribution endpoint with automatic cap at target
- Progress & percentage provided in responses

### 🤖 AI & Insights ✅ (Rule-based + Enhanced Path)
- Public quick categorization endpoint
- Authenticated smart categorization endpoint
- Financial advice & spending insights (rule-based fallback; AI-ready abstraction)
- In-memory caching layer for AI responses & stats endpoints

### 📊 Upcoming UI (Planned)
- Budget utilization rings (color-coded over-limit)
- Goal progress radial charts & contribution modal
- Dashboard KPI widgets (top category, monthly totals, averages)

---

## 🧱 Domain Models (Simplified)

Budget:
```
(id, user_id, period, total_limit, spent_amount, created_at, notes)
Unique: (user_id, period)
```
Goal:
```
(id, user_id, name, target_amount, current_amount, target_date, created_at, notes)
Unique (user_id, name) via composite index (logical uniqueness enforced/tests)
```
Expense links to budgets indirectly through period aggregation.

Auto Sync Logic:
- Any expense mutation (create/update/delete) triggers recomputation of that budget's `spent_amount` (aggregate of expenses for its period)
- If an expense's period changes, both old & new budgets recompute

Edge Behaviors:
- Budget utilization can exceed 1.0 (over-limit; UI highlights planned)
- Reducing a goal's target below `current_amount` does NOT clamp (documented, test-covered)

---

## 🔌 API Endpoints (Core New Additions)
```
# Budgets
GET    /api/budgets                -> list user's budgets
POST   /api/budgets                -> create { period, total_limit, notes? }
GET    /api/budgets/{id}           -> retrieve
PUT    /api/budgets/{id}           -> update (limit/notes)
DELETE /api/budgets/{id}           -> delete

# Goals
GET    /api/goals                  -> list
POST   /api/goals                  -> create { name, target_amount, target_date?, notes? }
GET    /api/goals/{id}             -> retrieve
PUT    /api/goals/{id}             -> update
DELETE /api/goals/{id}             -> delete
POST   /api/goals/{id}/contribute  -> { amount } (caps at target)

# AI / Insights
POST   /api/ai/categorize          -> public quick categorization
POST   /api/ai/categorize-smart    -> auth smart categorization
POST   /api/ai/financial-advice    -> personalized advice (auth)
GET    /api/ai/spending-insights   -> insights & patterns (auth)
GET    /api/cache/stats            -> cache metrics
```
Response Enhancements:
- Budget endpoints include: `remaining`, `utilization` (spent/limit)
- Goal endpoints include: `progress_percent`

---

## 🧪 Testing Infrastructure (Updated)
- Alembic migrations applied once per session; schema verified at head
- SQLite file DB recreated fresh each test session; per-test SAVEPOINT ensures isolation even across commits
- Unique email generation fixture prevents cross-test collisions
- Comprehensive tests:
  - Auth (signup/login/refresh/logout/security)
  - Password policy & token expiry
  - Expenses CRUD
  - Budget CRUD + uniqueness + over-limit utilization
  - Automatic budget sync on expense lifecycle & period movement
  - Goals CRUD + contribution capping + target reduction behavior
  - AI endpoints & caching (categorization, advice, insights)
- Current suite: 43 passed, 1 skipped (optional rate limit), 4 benign warnings (to refine later)

Planned Test Improvements:
- Convert return-value style ML system tests to assertions (remove warnings)
- Add performance regressions (budget recalculation complexity)

---

## 🛠️ Technology Stack

| Category | Technology | Status |
|----------|------------|--------|
| Frontend | React 18, Router | ✅ Deployed |
| Backend  | FastAPI, SQLAlchemy 2 | ✅ Deployed |
| Auth     | JWT + Rotating Refresh | ✅ |
| Domain   | Expenses, Budgets, Goals | ✅ |
| AI Layer | Rule-based + AI-ready abstraction | ✅ Base |
| Caching  | In-memory AI advice/cache | ✅ |
| DB       | PostgreSQL (prod), SQLite (tests) | ✅ |
| Migrations | Alembic | ✅ |
| Testing  | Pytest w/ transactional isolation | ✅ |

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+ (for backend development)
- Git
- VS Code (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PCSchmidt/generative-ai-budget-tracker.git
   cd generative-ai-budget-tracker
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   # For frontend development (React web app)
   cd frontend
   npm start
   
   # For backend development (FastAPI)
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   
   # For full-stack development (Docker)
   docker-compose up --build
   ```

4. **Open your browser**
   - **Frontend**: `http://localhost:3000` (React web app)
   - **Backend API**: `http://localhost:8000` (FastAPI + Swagger docs)
   - **Live Demo**: Visit the deployed version on Vercel

### 🎯 Try the Authentication System
- **Signup**: Create a new account with email and password
- **Login**: Test the working password visibility toggles
- **Navigation**: Experience the protected route system

## 📁 Project Structure

```
generative-ai-budget-tracker/
├── 🎯 src/                     # React application source
│   ├── components/
│   │   ├── auth/              # ✅ ProtectedRoute component
│   │   └── ui/                # ✅ Professional UI components
│   ├── screens/
│   │   ├── auth/              # ✅ Login/Signup with password toggles
│   │   ├── dashboard/         # ✅ Dashboard with welcome UI
│   │   └── LandingPage.js     # ✅ Professional landing page
│   ├── contexts/
│   │   └── AuthContext.js     # ✅ Complete auth state management
│   ├── services/
│   │   └── api.js             # ✅ API service ready for backend
│   ├── styles/
│   │   └── GlobalStyles.css   # ✅ Modern fintech design system
│   └── theme/
│       └── index.js           # ✅ Professional color palette
├── 🔧 backend/                # FastAPI backend (ready)
│   ├── app/
│   │   ├── auth/              # ✅ User models and mock DB
│   │   ├── api/               # 🚧 Ready for endpoints
│   │   └── services/          # 🚧 Ready for AI integration
│   ├── Dockerfile             # ✅ Production ready
│   └── requirements.txt       # ✅ Dependencies defined
├── 🐳 Docker/                 # Containerization ready
├── 📚 docs/                   # Comprehensive documentation
└── 🚀 .github/                # Deployment configs
```

## 🔑 Key Achievements

### ✅ **Professional Authentication**
- **Working Password Toggles**: Industry-standard Show/Hide buttons on both login and signup forms
- **Clean UI Implementation**: HTML buttons with proper styling instead of unreliable emoji icons
- **Cross-Platform Compatibility**: Works consistently across all browsers and devices
- **Accessibility**: Clear text labels for screen readers and keyboard navigation

### ✅ **Modern Fintech Design**
- **Professional Color Palette**: Carefully chosen colors for financial applications
- **Inter Font Integration**: Professional typography for better readability
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Glass Morphism Effects**: Modern backdrop blur and transparency effects

### ✅ **Production-Ready Architecture**
- **React 18 Best Practices**: Modern hooks, context API, and component patterns
- **Clean Code Structure**: Modular components with clear separation of concerns
- **Error Handling**: Comprehensive error states and user feedback
- **Performance Optimized**: Efficient rendering and state management

## 🎯 Development Phases (Revised)

### ✅ Phase 1: Authentication & UI Foundation
Completed previously.

### ✅ Phase 2: Core Financial Domain (Backend Complete)
- Budgets model + CRUD
- Goals model + CRUD + contributions
- Automatic budget spent sync with expenses
- Extended analytics utilities (basis for dashboard KPIs)

### 🚧 Phase 3: AI Enhancement & Frontend Visualization
- Implement live model integrations (Groq / HF) for advice & advanced categorization
- Frontend dashboards for budgets/goals (utilization rings, progress charts)
- Advanced spending analysis charts (Victory / Chart.js)

### 🔜 Phase 4: Production Hardening & PWA Enhancements
- Rate limiting (enable slowapi in prod)
- Security headers & monitoring
- Performance profiling & caching strategy tuning

---

## 📊 Roadmap Snapshot
- [x] Budgets domain & sync
- [x] Goals domain & contributions
- [x] AI endpoints functional with caching
- [ ] Frontend budget & goal UI widgets
- [ ] Live AI integration (Groq key usage)
- [ ] Visualization layer (charts)
- [ ] Performance tests & warnings cleanup

---

## 🧪 Sample Budget Response (Illustrative)
```json
{
  "id": 12,
  "period": "2025-08",
  "total_limit": 1500.0,
  "spent_amount": 1625.5,
  "remaining": -125.5,
  "utilization": 1.0837,
  "notes": "Summer travel"
}
```
Over-limit budgets show utilization > 1; UI will highlight.

## 🧪 Sample Goal Contribution Response
```json
{
  "id": 7,
  "name": "Emergency Fund",
  "target_amount": 5000.0,
  "current_amount": 5000.0,
  "progress_percent": 100.0,
  "capped": true
}
```

---

## ⚙️ Automatic Budget Recalculation (Detail)
Trigger Points:
1. Expense created -> add amount to budget period aggregate
2. Expense updated -> recompute old (if period changed) & new period budgets
3. Expense deleted -> subtract via full recompute

Why recompute instead of incremental adjust?
- Ensures correctness if historical data mutates (simpler & safe for current scale). Potential optimization: delta adjustments + periodic integrity checks.

---

## 🧩 Contributing (Unchanged Core Flow)
...existing code...

## 📈 Performance & Metrics (Planned Updates)
Add budget sync performance counters & cache hit ratios to README after instrumentation.

---

## 🔐 Security Notes (Incremental)
- Refresh token rotation & revocation
- Password policy enforced via Pydantic validator
- Future: Per-endpoint rate limiting once slowapi installed

---

## 📄 License & Acknowledgments
...existing code...

---

> Continue with frontend visualization tasks next: budget utilization components & goal progress UI.
