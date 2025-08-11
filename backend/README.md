# Backend Development

## Database (Low/No Cost Strategy)

Default dev DB uses SQLite file `budget_dev.db` (no external cost). Set `DATABASE_URL` to Postgres only when ready to deploy/monetize.

Example env for local Postgres (optional):
```
DATABASE_URL=postgresql://budget_user:budget_pass@localhost:5432/budget_tracker
```

## Alembic Migrations

Generate new migration:
```
cd backend
alembic revision -m "add new table"
```
Apply migrations:
```
alembic upgrade head
```
Downgrade (rollback last):
```
alembic downgrade -1
```
Autogenerate (after model changes):
```
alembic revision --autogenerate -m "describe change"
```

## First-Time Setup
1. Install deps: `pip install -r requirements.txt`
2. Run migrations: `alembic upgrade head`
3. Start server: `uvicorn app.main:app --reload`

SQLite file will be created automatically. Safe to delete for a clean slate.
