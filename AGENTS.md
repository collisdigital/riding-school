# Riding School Progress Tracker - Agent Onboarding Guide

## High-Level Details
- **Project Type**: Multi-tenant SaaS platform for riding schools.
- **Stack**:
  - **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic, Alembic.
  - **Frontend**: React 19, Vite, TypeScript, Tailwind CSS v4.
  - **Database**: PostgreSQL 16.
  - **E2E**: Playwright.
  - **Infrastructure**: Docker Compose.
- **Repository Size**: Medium.
- **Architecture**: Monolithic repository with separate backend and frontend services.

## Build & Validation Instructions

### 1. Bootstrap & Run
To start the entire application (Backend on 8000, Frontend on 5173, DB on 5432):
```bash
docker-compose up --build
```
*Notes:*
- *Backend startup runs Alembic migrations automatically via `backend/start.sh` (`alembic upgrade head`) before starting Uvicorn.*
- *This is required for E2E tests and full manual verification.*

### 1.1 Clean Build Reset (No Data)
To fully reset Docker state (containers, images, networks, and volumes, including PostgreSQL data):
```bash
docker system prune -a --volumes -f
```

Then rebuild:
```bash
docker-compose up --build
```

### 2. Backend (Local Development)
*Prerequisites: Python 3.12, pip*

**Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Linting & Formatting:**
*Always run before committing. Verify changes with `--check`.*
```bash
ruff check . --fix
ruff format .
ruff format --check .
```

**Testing:**
*Uses SQLite in-memory DB by default. No external DB required.*
```bash
PYTHONPATH=. pytest
```
*Expected Output: All tests passed. Ignore deprecation warnings.*

**Run API outside Docker:**
```bash
# Optional sqlite for local app run
export DATABASE_URL=sqlite:///./local.db
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend (Local Development)
*Prerequisites: Node.js (v20+ recommended), npm*

**Setup:**
```bash
cd frontend
npm install
```

**Linting & Formatting:**
*Always run before committing. Verify changes.*
```bash
npm run lint
npm run format
npx prettier --check .
```

**Testing (Unit/Component):**
```bash
npm test -- --run
```

### 4. End-to-End Tests & Pre-Commit Debugging Workflow
*Prerequisites (outside Docker): Backend and Frontend running locally at `http://localhost:8000` and `http://localhost:5173`.*

**Setup & Execution (outside Docker):**
```bash
# backend terminal
cd backend
source venv/bin/activate
export DATABASE_URL=sqlite:///./local.db
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# frontend terminal
cd frontend
npm install
npm run dev

# e2e terminal
cd e2e
npm install
npx playwright install chromium
npx playwright test
```

**Run Tests (Docker one-shot, auto shutdown):**
```bash
docker compose --profile e2e up --build --abort-on-container-exit --exit-code-from e2e e2e
```

**E2E Test Execution:**
Run the full suite locally:
```bash
cd e2e
npx playwright test
```

Run tests for a specific file or feature:
```bash
npx playwright test tests/auth.spec.ts
```

**Console Log Capture on Failure:**
A global fixture is configured to automatically listen for browser console errors. If an error occurs, it will be logged to the terminal with the prefix `BROWSER ERROR:`.
- **Requirement:** Watch the terminal output during test execution.
- **Implementation:** This is handled via `e2e/fixtures.ts`. If you are creating manual browser contexts (e.g., for multi-tenant tests), ensure you attach the listener or use the provided helpers.

**Artifact Analysis:**
If a test fails, Playwright automatically retains traces and screenshots. To inspect them:
```bash
npx playwright show-report
```
Use this report to view screenshots and trace files of failed steps.

**The "Check-Before-Commit" Rule:**
For any UI-heavy feature (like Drag-and-Drop or Multi-tenant Auth), the agent **MUST** run the headless browser suite and confirm **zero console errors** before finalizing the task.

## Project Layout

### Backend (`backend/`)
- `app/main.py`: Application entry point.
- `app/api/`: Route handlers (e.g., `auth.py`, `schools.py`).
- `app/models/`: SQLAlchemy models. **Critical**: New models must use `TenantMixin`.
- `app/schemas/`: Pydantic schemas.
- `app/core/`: Configuration (`config.py`) and security.
- `alembic/`: Database migration scripts.
- `tests/`: Pytest suite.

### Frontend (`frontend/`)
- `src/main.tsx`: Entry point.
- `src/App.tsx`: Main router and layout setup.
- `src/pages/`: Page components (e.g., `DashboardPage.tsx`).
- `src/layouts/`: Shared layouts (Auth, Protected).
- `vite.config.ts`: Vite configuration.

### E2E (`e2e/`)
- `tests/`: Playwright specs. `auth.spec.ts` covers the main user journey.
- `fixtures.ts`: Global test fixtures (includes console error listener).

## Critical Implementation Guidelines

1.  **Multi-Tenancy**:
    - All school-specific models **MUST** inherit from `TenantMixin` (`app.models.base`) to enforce `school_id`.
    - API endpoints returning school data **MUST** filter by `current_user.school_id`.
    - Use `deps.get_current_active_school_user` for endpoints requiring a school context.

2.  **Authentication & Permissions**:
    - Auth uses HttpOnly cookies (`access_token`).
    - Use `deps.get_current_user` for context-agnostic endpoints (e.g., onboarding).
    - **Permissions**: Use `deps.RequirePermission("permission_name")` for endpoints requiring specific access rights (e.g., `riders:delete`). Do NOT check role names directly (e.g., `if user.role == "ADMIN"`).
    - Permissions are seeded via `backend/app/core/seed.py`.

3.  **Database & Migrations**:
    - Use SQLAlchemy 2.0 style queries (`db.execute(select(Model)...)` or `db.query(Model)`).
    - Docker backend startup applies migrations automatically (`alembic upgrade head`) before the API starts.
    - **Migrations**: Any change to `app/models` requires an Alembic migration.
        - Generate: `alembic revision --autogenerate -m "message"`
        - Apply: `alembic upgrade head`
    - Do NOT rely on `Base.metadata.create_all` for schema updates; use migrations.

4.  **Workflows**:
    - **TDD**: Write a failing backend test or frontend component test before implementing features.
    - **Validation**: If you modify the backend, run `pytest`. If you modify the frontend, run `npm test`.
    - **Verification**: Trust the tests. If `pytest` passes, the logic is likely sound.

## Common Issues & Fixes
- **Frontend 401s**: Ensure `axios.defaults.withCredentials = true` is set (it is in `main.tsx`).
- **DB Connection**: If running tests locally, `sqlite` is used. If running via Docker, `postgres` is used. Ensure `DATABASE_URL` is set correctly in `.env` or environment variables if deviating from defaults.

## File Inventory (Root)
- `AGENTS.md`: This file.
- `docker-compose.yml`: Service orchestration.
- `README.md`: General project info.
- `backend/`: Backend service.
- `frontend/`: Frontend service.
- `e2e/`: End-to-end tests.

**TRUST THESE INSTRUCTIONS**: Do not search for build/test commands unless these instructions fail or are incomplete.
