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

Production Checklist
Backend (Railway)
- [ ] SECRET_KEY set to a strong random value (not default)
- [ ] DATABASE_URL points to production Postgres and is reachable
- [ ] CORS allow_origins includes Vercel domains (https://<your-app>.vercel.app)
- [ ] Optional AI keys configured: HUGGINGFACE_API_KEY, GROQ_API_KEY
- [ ] /health returns { status: "healthy" }

Frontend (Vercel)
- [ ] Production build uses Railway API base URL (handled in src/services/api.js)
- [ ] Environment variables configured if needed
- [ ] Deployment succeeds; site loads over HTTPS

Security
- [ ] JWT algorithm HS256 confirmed; SECRET_KEY rotation policy documented
- [ ] CORS restricted to exact domains; no wildcards in production
- [ ] No secrets committed; .env files excluded

Observability
- [ ] Enable platform logs/metrics (Railway + Vercel)
- [ ] Capture 4xx/5xx rates and add alerting (optional)

QA Validation (Post-Deploy)
- [ ] Login from Vercel UI triggers POST https://<railway-domain>/auth/login → 200
- [ ] Local Storage contains accessToken and user
- [ ] GET /api/expenses → 200 with Authorization header
- [ ] POST /api/ai/financial-advice → 200 with expected fields (main_advice, action_items, confidence)
- [ ] GET /api/ai/spending-insights → 200 with category_breakdown
- [ ] No CORS or mixed-content errors in Console

Test Plan (Local)
- Visit http://localhost:3000/login and sign in with demo@budgettracker.com / password123
- Verify POST http://localhost:8000/auth/login → 200 with { access_token, user }
- Navigate to /dashboard; verify expenses and AI panels render without runtime errors

Environment & Config (Production)
- Railway
  - SECRET_KEY
  - DATABASE_URL
  - Optional: HUGGINGFACE_API_KEY, GROQ_API_KEY
  - CORS allow_origins include Vercel domains
- Vercel
  - NODE_ENV=production
  - Uses production API base URL (src/services/api.js logic)

Rollback Plan
- Revert this commit and redeploy previous stable frontend/backend
- If auth/API fails, temporarily disable protected routes for public landing only

Known Follow-ups
- Centralized 401 auto-logout/toast in src/services/api.js
- Remove debug logs
- Add charts and richer AI categorization UI

Screenshots/Proof
- DevTools Network: POST /auth/login 200; AI endpoints return 200 with expected JSON

