## Frontend Consolidation (2025-08-12)

This project accumulated multiple frontend folders during iterative development. To remove ambiguity and simplify builds, we consolidated the web app to a single source of truth.

### Decision
- Canonical frontend: root `src/` with root `package.json` (React 18 + react-scripts).
- Archived folders:
  - `archive/frontend-legacy-2025-08-12/` (moved from `frontend/`)
  - `docs/prototypes/web-frontend/` (moved from `web-frontend/`)

### Why
- Duplicate React trees (`/src` and `/frontend/src`) caused confusion during local runs and CI.
- The root app aligns with the documented Phase 1/2 web architecture (AuthContext, ProtectedRoute, services/api.js, design system).
- The `web-frontend/` directory contained static prototype pages only.

### What changed
- The root README now states the canonical location and updated start commands.
- `frontend/` and `web-frontend/` were moved to archival locations (history preserved via `git mv`).

### How to run (web)
```bash
# from repo root
npm install
npm start
# Frontend at http://localhost:3000
```

### How to run (backend)
```bash
# from repo root
source .venv/Scripts/activate  # Windows Git Bash
SECRET_KEY=your-strong-key \
  ACCESS_TOKEN_EXPIRE_MINUTES=60 \
  BCRYPT_ROUNDS=10 \
  python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
# API at http://127.0.0.1:8000
```

### If you need something from the archives
- Review and cherry-pick differences from `archive/frontend-legacy-2025-08-12/` into root `src/`.
- Prototype HTML is under `docs/prototypes/web-frontend/`.

### Future guardrail (optional)
- Add a CI check that fails if another top-level `package.json` with `react-scripts` or a duplicate `src/` appears. This prevents reintroducing multiple web apps inadvertently.
