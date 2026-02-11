# Agent Collaboration Guide: Riding School Progress Tracker

## Tech Stack Versions
- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2.0, Pydantic v2
- **Frontend**: Vite, React, TypeScript, Tailwind CSS v4
- **Database**: PostgreSQL 16
- **Testing**: Pytest (Backend), Vitest (Frontend), Playwright (E2E)

## Key Commands

### Development
- `docker-compose up --build`: Start the entire stack.
- `docker-compose logs -f [service]`: Follow logs for a specific service.

### Testing
- `docker-compose run -e PYTHONPATH=. backend pytest`: Run backend unit/integration tests.
- `docker-compose run frontend npm run test -- --run`: Run frontend component tests.
- `cd e2e && npx playwright test`: Run full E2E journey and leak tests.

### Linting & Formatting
#### Backend (Ruff)
- `ruff check .`: Check for linting errors.
- `ruff format .`: Format code.

#### Frontend (ESLint + Prettier)
- `npm run lint`: Check for linting errors.
- `npm run format`: Format code using Prettier.

## AI Agent Instructions
As an AI agent working on this codebase, you MUST adhere to the following workflow:

1.  **Safety First**: Before making any functional changes, run the existing test suite (`pytest` and `playwright`) to establish a baseline.
2.  **Linting & Formatting**: 
    - You MUST run `ruff format .` and `ruff check .` for backend changes.
    - You MUST run `npm run format` and `npm run lint` for frontend changes.
3.  **Multi-Tenancy Integrity**: 
    - Every new database model (except User/School core) MUST use `TenantMixin` from `app.models.base`.
    - Every API endpoint MUST filter queries by `current_user.school_id`.
    - NEVER return data that doesn't belong to the authenticated user's school.
4.  **Test-Driven Development**:
    - When adding a feature, add a corresponding backend test in `backend/tests/`.
    - For UI features, update the E2E suite in `e2e/tests/` to cover the new journey.
    - Always run `npx playwright test` after UI changes to ensure the "Multi-tenant leak test" still passes.
4.  **Schema and Migrations**:
    - Do not modify `app/models/` without approval.
    - Use Alembic for migrations (when implemented). For now, `Base.metadata.create_all` is used on startup.
5.  **Authentication**:
    - Use `deps.get_current_active_school_user` for endpoints requiring a school context.
    - Use `deps.get_current_user` for onboarding endpoints where a school might not exist yet.

## Project Structure
- `backend/app/api`: Route handlers, organized by feature.
- `backend/app/models`: SQLAlchemy models (use `TenantMixin` for isolation).
- `backend/app/schemas`: Pydantic models for validation.
- `frontend/src/pages`: Top-level route components.
- `frontend/src/layouts`: Shared UI wrappers (e.g., `AuthLayout`).
- `e2e/tests`: Playwright specs, including critical security leak tests.
