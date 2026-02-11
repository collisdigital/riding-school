# Agent Collaboration Guide: Riding School Progress Tracker

## Tech Stack Versions
- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2.0, Pydantic v2
- **Frontend**: Vite, React, TypeScript, Tailwind CSS v4
- **Database**: PostgreSQL 16
- **Testing**: Pytest (Backend), Vitest + React Testing Library (Frontend)

## Key Commands

### Docker (Preferred for Consistency)
- `docker-compose up --build`: Start the entire stack
- `docker-compose run -e PYTHONPATH=. backend pytest`: Run backend tests
- `docker-compose run frontend npm run test -- --run`: Run frontend tests

### Backend (Local)
- `pytest`: Run backend tests (requires `PYTHONPATH=.`)
- `uvicorn app.main:app --reload`: Start dev server

### Frontend (Local)
- `npm run dev`: Start Vite dev server
- `npm run test`: Run Vitest
- `npm run build`: Build for production

## Development Boundaries
1. **Schema Changes**: Do not modify database schemas in `app/models/` without explicit user approval.
2. **Migrations**: Use Alembic (to be added) for all database schema changes.
3. **Typing**: Strict TypeScript and Python type hinting is required.
4. **Testing**: New features MUST include corresponding tests.
5. **Tailwind**: Use CSS-first configuration for Tailwind v4. Prefer standard utility classes.

## Project Structure
- `backend/app/api`: Route handlers
- `backend/app/models`: SQLAlchemy models
- `backend/app/schemas`: Pydantic models
- `frontend/src/components`: UI components
- `frontend/src/hooks`: Custom React hooks
