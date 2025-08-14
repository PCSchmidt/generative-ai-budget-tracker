# Flip frontend to live backend (Vercel ↔ Railway)

Follow these steps to connect the production SPA to the live FastAPI API on Railway.

## 1) Confirm backend health

- Open the Railway backend service, copy the public domain, and visit:
  - `https://<your-backend-domain>/health`
- Expect JSON with `status: healthy` and a non-null `uptime_seconds`.

## 2) Ensure CORS allows your frontend

In Railway > backend > Variables set one of:

- `FRONTEND_ORIGINS=https://<your-vercel-domain>`
  - Example: `https://generative-ai-budget-tracker.vercel.app`

OR (to allow all Vercel preview/prod URLs):

- `FRONTEND_ORIGIN_REGEX=^https://.*\.vercel\.app$`

Redeploy backend if variables changed.

## 3) Set Vercel environment variables

Project Settings → Environment Variables (Production):

- `REACT_APP_API_BASE_URL=https://<your-backend-domain>`
- `REACT_APP_ALLOW_MOCK_PROD=false`

Redeploy the frontend.

## 4) Verify in production

- Open the SPA. A small badge in the lower-right briefly shows:
  - “Connected: Live API” if the backend is used.
- Log in / sign up and navigate to dashboard and expenses.

If the badge shows “Using Mock API”, re-check Step 1–3.
