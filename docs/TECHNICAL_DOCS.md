# AI Budget Tracker - Technical Documentation

## 🏗️ Architecture Overview

### Current Implementation Status

**✅ PHASE 1 COMPLETE: Authentication & UI Foundation**

The AI Budget Tracker follows a modern web application architecture with a React frontend and FastAPI backend, designed for scalability and maintainability.

## 📱 Frontend Architecture

### Technology Stack
- **React 18.2.0**: Modern React with functional components and hooks
- **React Router v6**: Client-side routing with protected routes
- **Context API**: Global state management for authentication
- **Modern CSS**: Custom styling with CSS-in-JS and global styles
- **PWA Ready**: Progressive Web App capabilities

### Component Architecture

```
src/
├── components/
│   ├── auth/
│   │   └── ProtectedRoute.js     # Route protection wrapper
│   └── ui/
│       ├── Button.js             # Reusable button component
│       ├── Card.js               # Card container component
│       └── LoadingSpinner.js     # Loading state component
├── screens/
│   ├── auth/
│   │   ├── LoginScreen.js        # Login form with password toggle
│   │   └── SignupScreen.js       # Registration form
│   ├── dashboard/
│   │   └── DashboardScreen.js    # Main application dashboard
│   └── LandingPage.js            # Public homepage
├── contexts/
│   └── AuthContext.js            # Authentication state management
├── services/
│   └── api.js                    # API communication layer
├── styles/
│   └── GlobalStyles.css          # Global CSS styles
└── theme/
    └── index.js                  # Design system tokens
```

### Authentication Flow

```mermaid
graph TD
    A[User visits app] --> B{Authenticated?}
    B -->|No| C[LandingPage]
    B -->|Yes| D[DashboardScreen]
    C --> E[Login/Signup]
    E --> F[API Authentication]
    F --> G[Store JWT tokens]
    G --> D
    D --> H[Protected Routes]
```

### Key Components

#### 1. Authentication Context (`AuthContext.js`)
- **Purpose**: Global authentication state management
- **Features**:
  - JWT token storage in localStorage
  - Automatic token refresh
  - User session persistence
  - Error handling and loading states

#### 2. Protected Route Component (`ProtectedRoute.js`)
- **Purpose**: Route-level authentication guard
- **Features**:
  - Automatic redirect to login if not authenticated
  - Loading state during authentication check
  - Clean component composition

#### 3. Password Toggle Implementation
- **Technology**: HTML buttons with React state
- **Accessibility**: Clear text labels for screen readers
- **Cross-platform**: Works consistently across all browsers

## 🔧 Backend Architecture

### Technology Stack
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **JWT**: Token-based authentication
- **Docker**: Containerized deployment

### Project Structure

```
backend/
├── app/
│   ├── auth/
│   │   ├── models.py             # User authentication models
│   │   └── mock_db.py            # Development database mock
│   ├── api/
│   │   └── endpoints/            # API route handlers (ready)
│   ├── services/
│   │   └── ai_service.py         # AI integration layer (ready)
│   └── core/
│       ├── config.py             # Application configuration
│       ├── database.py           # Database connection
│       └── security.py           # Security utilities
├── Dockerfile                    # Production container
├── requirements.txt              # Python dependencies
└── start.sh                     # Startup script
```

### Database Schema

#### User Model
```python
class User:
    id: int (Primary Key)
    email: str (Unique)
    username: str (Unique)
    hashed_password: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
```

## 🎨 Design System

### Color Palette

```css
/* Primary Brand Colors */
--primary-900: #0f172a;    /* Dark slate - headers */
--primary-800: #1e293b;    /* Medium slate - navigation */
--primary-700: #334155;    /* Light slate - secondary text */

/* Accent Colors */
--accent-600: #2563eb;     /* Primary CTA buttons */
--accent-500: #3b82f6;     /* Links and interactions */
--accent-400: #60a5fa;     /* Hover states */

/* Financial Status Colors */
--success-600: #059669;    /* Positive amounts */
--error-600: #dc2626;      /* Negative amounts */
--warning-600: #d97706;    /* Alerts */
```

### Typography
- **Font Family**: Inter (Google Fonts)
- **Sizes**: 12px (xs) to 48px (5xl)
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Spacing System
- **Base Unit**: 4px
- **Scale**: xs(4px), sm(8px), md(16px), lg(24px), xl(32px), 2xl(48px)

## 🔐 Security Implementation

### Frontend Security
- **Token Storage**: Secure localStorage with automatic cleanup
- **Input Validation**: Client-side form validation
- **XSS Protection**: React's built-in XSS protection
- **HTTPS Only**: Production deployment with SSL

### Backend Security (Ready)
- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure token generation and validation
- **CORS Configuration**: Proper cross-origin request handling
- **Rate Limiting**: API endpoint protection
- **Input Sanitization**: SQLAlchemy ORM protection

## 🚀 Deployment Architecture

### Current Setup
- **Frontend**: Vercel deployment ready
- **Backend**: Railway deployment configured
- **Database**: PostgreSQL on Railway
- **CDN**: Vercel Edge Network

### Environment Configuration

```bash
# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development

# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/budget_tracker
SECRET_KEY=your-secret-key
HUGGINGFACE_API_KEY=your-hf-key
GROQ_API_KEY=your-groq-key
```

## 🧪 Testing Strategy

### Current Testing
- **Manual Testing**: Comprehensive UI/UX testing
- **Browser Testing**: Cross-browser compatibility
- **Responsive Testing**: Mobile and desktop layouts
- **Authentication Flow**: Complete user journey testing

### Future Testing (Phase 2)
- **Unit Tests**: Jest + React Testing Library
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Cypress for complete user flows
- **Performance Tests**: Lighthouse auditing

## 📊 Performance Optimization

### Current Optimizations
- **Code Splitting**: React.lazy for route-based splitting
- **Image Optimization**: Vercel automatic image optimization
- **Bundle Optimization**: Modern build tools
- **Caching**: Browser caching strategies

### Future Optimizations (Phase 2)
- **State Management**: Optimized Context usage
- **API Caching**: React Query implementation
- **Database Indexing**: PostgreSQL optimization
- **CDN Integration**: Static asset optimization

## 🔄 Development Workflow

### Git Strategy
- **Main Branch**: Production-ready code
- **Feature Branches**: Individual feature development
- **Commit Convention**: Conventional commits format
- **PR Process**: Code review and testing

### Build Process
1. **Development**: `npm start` for hot reload
2. **Testing**: `npm test` for unit tests
3. **Building**: `npm run build` for production
4. **Deployment**: Automatic via Vercel/Railway

## 🚧 Future Development Phases

### Phase 2: Core Features
- Expense management CRUD operations
- Category system implementation
- Dashboard data visualization
- Backend API integration

### Phase 3: AI Integration
- Hugging Face expense categorization
- Groq financial advice generation
- Pattern recognition algorithms
- Goal tracking with predictions

### Phase 4: Advanced Features
- Real-time notifications
- Data export/import
- Advanced analytics
- Mobile app deployment

## 📚 Code Quality Standards

### Frontend Standards
- **ESLint**: JavaScript linting rules
- **Prettier**: Code formatting
- **TypeScript**: (Future migration planned)
- **Component Patterns**: Functional components with hooks

### Backend Standards
- **Black**: Python code formatting
- **Pylint**: Python linting
- **Type Hints**: Full type annotation
- **FastAPI Best Practices**: Async/await patterns

## 🔧 Development Tools

### Required Tools
- **Node.js 18+**: JavaScript runtime
- **Python 3.11+**: Backend development
- **Git**: Version control
- **VS Code**: Recommended editor
- **Docker**: Containerization (optional)

### Recommended Extensions
- **ES7+ React/Redux/React-Native snippets**
- **Prettier - Code formatter**
- **GitLens**
- **Python**
- **Thunder Client** (API testing)

---

*This documentation reflects the current state of the AI Budget Tracker as of Phase 1 completion. Updates will be made as new phases are implemented.*
