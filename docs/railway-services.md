# Railway Services: Backend API vs Postgres

This project is designed with two separate Railway services:

- Backend (FastAPI) — your application API, deployed from `backend/Dockerfile.railway` using the project-level `railway.toml` at repo root.
- Postgres — a managed PostgreSQL database service provided by Railway.

Having both is expected and correct: the backend connects to Postgres via `DATABASE_URL` and should not bundle a database container within the API image in production.

## Why you see two builds
- "backend" service builds your Python API image and runs `./start.sh` (Alembic migrations + Uvicorn).
- "Postgres" service is a prebuilt database image maintained by Railway; it doesn’t rebuild your app. Railway may show log entries there (including warnings) even when the backend deploy fails/succeeds independently.

## Collation mismatch warnings
You may see warnings like:

> WARNING: database "railway" has a collation version mismatch

These are informational unless migrations fail. If desired, you can refresh collations:

- For new/empty DBs: recreate the DB with the desired collation/locale.
- For existing data: follow PostgreSQL docs to `REINDEX` or `ALTER DATABASE ... REFRESH COLLATION VERSION`, being mindful of downtime.

Our `start.sh` runs Alembic and treats these as warnings unless Alembic errors.

## Which railway.toml is used?
- Root `railway.toml` — primary configuration when deploying the whole repo. It points to `backend/Dockerfile.railway`.
- `backend/railway.toml` — convenience config if you deploy from `backend/` directory only.

Both target the same backend runtime; they exist to support different workflows.

## Recommended workflow
1. Set service variables in Railway for the backend: `SECRET_KEY`, `DATABASE_URL`, `UVICORN_LOG_LEVEL` (optional), etc.
2. Trigger a backend redeploy from Railway UI (recommended if CLI is flaky) so the fixed Dockerfile is used.
3. Verify health:
   - `/ready` and `/health` should return 200
   - Alembic revision prints in logs
4. Flip the frontend to the live API URL and redeploy the frontend.

If backend deploy still fails, check the Build logs for Docker COPY path issues and Runtime logs for `app.main` import or Alembic connection errors.
