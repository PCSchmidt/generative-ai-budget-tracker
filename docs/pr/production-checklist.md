# Production Prep: Authentication & AI Dashboard Integration

Summary
- Wire up web login to real backend (/auth/login) and fix AI dashboard rendering.
- Confirm local end-to-end: login, protected routes, expenses, AI advice/insights.

Changes
- src/screens/auth/LoginScreen.web.js
  - Call AuthContext.login to POST /auth/login.
  - Navigate to /dashboard on success.
  - Validation, loading, and error display.
- src/screens/dashboard/DashboardScreen.js
  - Render advice.main_advice and action_items (fixes React runtime error: objects are not valid as a React child).
  - Safer handling for insights/advice responses; minor UI tweaks.
- backend/app/main.py (context)
  - Auth endpoints, AI endpoints, and CORS are ready for production; verified locally via DevTools.

Environment & Config (Production)
- Railway (backend)
  - SECRET_KEY: strong, random value
  - JWT_ALGORITHM: HS256 (default in app)
  - DATABASE_URL: postgres connection
  - HUGGINGFACE_API_KEY, GROQ_API_KEY (optional for advanced AI)
  - CORS allow_origins: include your Vercel domain(s)
- Vercel (frontend)
  - NODE_ENV=production (default)
  - API base URL is auto-switched in src/services/api.js (Railway in production)

Test Plan (Local)
- Go to http://localhost:3000/login
- DevTools → Network → Fetch/XHR → Sign in with demo@budgettracker.com / password123
  - Expect POST http://localhost:8000/auth/login → 200 with { access_token, user }
  - Local Storage contains accessToken and user
- Visit /dashboard
  - Cards render without errors
  - DevTools shows GET /api/expenses, POST /api/ai/financial-advice, GET /api/ai/spending-insights
  - Advice panel shows main_advice string and bullet action_items

Production Validation (Post-Deploy)
- Vercel app login hits Railway /auth/login and returns 200
- Protected GET /api/expenses returns 200 with Authorization header
- Dashboard shows advice and insights without runtime errors
- No CORS errors in Console

Rollback Plan
- Revert this branch if auth or dashboard regressions occur
- Re-deploy previous stable frontend and backend

Security & Hardening
- Ensure SECRET_KEY is not default
- Limit allow_origins to exact Vercel domains
- Monitor 401s and add auto-logout on unauthorized in a follow-up PR

Known Follow-ups
- Centralized 401 handler/toast in api.js
- Remove verbose console logs
- Charts for insights, more AI categories

Screenshots
- Local DevTools verified: POST /auth/login 200 with token and user

