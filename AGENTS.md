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
4.  **Test-Driven Development (TDD)**:
    - You are strongly advised to follow a TDD approach: write your tests FIRST before implementing new features to define the expected behavior and ensure they work as intended.
    - When adding a feature, add a corresponding backend test in `backend/tests/`.
    - For UI features, update the E2E suite in `e2e/tests/` to cover the new journey.
    - Always run `npx playwright test` after UI changes to ensure the "Multi-tenant leak test" still passes.
5.  **Test Coverage**:
    - Test coverage MUST NOT decrease when changes are made to the codebase.
    - Ideally, every change should increase the overall coverage percentage.
    - Run coverage reports locally before committing to verify you haven't introduced uncovered paths.
6.  **Schema and Migrations**:
    - Do not modify `app/models/` without approval.
    - Use Alembic for migrations (when implemented). For now, `Base.metadata.create_all` is used on startup.
7.  **Authentication**:
    - Use `deps.get_current_active_school_user` for endpoints requiring a school context.
    - Use `deps.get_current_user` for onboarding endpoints where a school might not exist yet.
8.  **Configuration & Security**:
    - Set `SECRET_KEY` to a secure value in non-development environments; `ENVIRONMENT` controls enforcement.
    - Use `SECURE_COOKIES=true` when deploying behind HTTPS to ensure auth cookies are secure.
    - Prefer DB pool settings (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`) for production deployments.
9.  **Database Writes**:
    - Wrap `db.commit()` in `try/except SQLAlchemyError`, call `db.rollback()` on failure, and surface an HTTP 500.
    - Avoid leaving partially flushed state (especially in multi-step create flows).
10. **E2E Test Setup**:
    - Playwright expects the frontend available at `http://localhost:5173` (use `docker-compose up --build` or run the Vite dev server).

## Project Structure
- `backend/app/api`: Route handlers, organized by feature.
- `backend/app/models`: SQLAlchemy models (use `TenantMixin` for isolation).
- `backend/app/schemas`: Pydantic models for validation.
- `frontend/src/pages`: Top-level route components.
- `frontend/src/layouts`: Shared UI wrappers (e.g., `AuthLayout`).
- `e2e/tests`: Playwright specs, including critical security leak tests.
