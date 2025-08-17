 # Deployment Guide (Vercel + Railway) — 2025-08-16

This guide documents the verified deployment path for AI Budget Tracker using a prebuilt backend image and a Vercel-hosted frontend.

## Overview

- Frontend: React (Vercel)
- Backend: FastAPI (Railway) with PostgreSQL
- Images: Built in GitHub Actions and pushed to GitHub Container Registry (GHCR)

## Backend (Railway)

1) Provision services
	- Create a “PostgreSQL” service (managed database)
	- Create a “Service from Image” for the FastAPI backend

2) Configure the backend service
	- Image: `ghcr.io/<owner>/<repo>:sha-<commit>` (or `:latest` once stable)
	- Start command (if needed): the container runs `backend/start.sh` which applies Alembic migrations and starts Uvicorn
	- Environment variables:
	  - `DATABASE_URL` (from the Railway Postgres service)
	  - `SECRET_KEY` (strong random string)
	  - `ACCESS_TOKEN_EXPIRE_MINUTES` (e.g., 30)
	  - `REFRESH_TOKEN_EXPIRE_DAYS` (e.g., 7)
	  - `FRONTEND_ORIGINS` or `FRONTEND_ORIGIN_REGEX` to allow your Vercel domain(s)
	- Expose HTTP port 8000 (Railway auto-detects)

3) Validate
	- Open the backend public URL and check `/health` and `/ready` return 200
	- Confirm logs show Alembic migrations applied

## Frontend (Vercel)

1) Project settings
	- Framework: Create React App or React static
	- Build Command: `npm run build`
	- Output: `build`

2) Environment variables (Production)
	- `REACT_APP_API_BASE_URL=https://<your-backend>.up.railway.app`
	- `REACT_APP_ALLOW_MOCK_PROD=false`

3) Deploy
	- Connect the GitHub repo and auto-deploy the `main` branch
	- After deploy, open DevTools Console and verify: `[ApiService] Base URL: ...`

## Auth & Signup Behavior

- Demo credentials (`demo@budgettracker.com` / `password123`) exist only in the mock service
- In production with Railway (Postgres), use the Signup form to create a real user; the record is stored and usable immediately (unless email verification is enabled)

## CORS and Common Issues

- Ensure CORS allows the Vercel origin. Either:
  - Set `FRONTEND_ORIGINS=https://<project>.vercel.app,https://<custom-domain>`
  - Or use `FRONTEND_ORIGIN_REGEX=^https:\/\/(.*\.)?vercel\.app$`
- If you see “Failed to fetch” from the frontend:
  - Confirm the base URL env var is set and the new build is live
  - Check the Network tab for CORS preflight failures
  - Verify the backend `/health` returns 200

## CI Images (Recommended)

- Use GitHub Actions to build and push `ghcr.io/<owner>/<repo>:sha-<commit>` and `:latest`
- In Railway, reference a specific `:sha-<commit>` to deploy deterministically

## Rollback

- Frontend: redeploy previous Vercel build
- Backend: switch Railway image tag back to the last good `:sha-<commit>`

## Appendix: Quick Checks

- Backend: `/health` shows DB connection OK; `/ready` indicates app readiness
- Frontend: Console prints `[ApiService] Base URL: ...` and signup/login work end-to-end
