# Riding School Progress Tracker

A production-grade multi-tenant SaaS platform for tracking rider progress through various grades.

## Core Features
- **Multi-tenancy**: Secure isolation between different riding schools.
- **Onboarding**: Self-service registration and school creation.
- **Rider Management**: Track riders and their achievements per school.
- **Auth**: JWT-based authentication with granular Role-Based Access Control (RBAC).

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the App
1. Clone the repository.
2. Run `docker-compose up --build`.
   - *Note: This will automatically run database migrations on startup.*
3. Open [http://localhost:5173](http://localhost:5173) to see the landing page.
4. Access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## Database Management

The project uses **Alembic** for database schema migrations.

### Running Migrations Manually
If you need to apply migrations manually (e.g., during development without restarting the container):
```bash
docker-compose run backend alembic upgrade head
```

### Creating a New Migration
When you modify SQLAlchemy models in `backend/app/models`, generate a new migration file:
```bash
docker-compose run backend alembic revision --autogenerate -m "Description of changes"
```
Review the generated file in `backend/alembic/versions/` before committing.

## Testing

### End-to-End Tests (Playwright)
E2E tests verify the full user journey and multi-tenant isolation.
```bash
# Ensure the app is running first
# In a new terminal:
cd e2e
npm install
npx playwright test
```

### Backend Tests (Pytest)
```bash
# Run tests locally (requires python env)
cd backend
PYTHONPATH=. pytest

# Or via Docker
docker-compose run -e PYTHONPATH=. backend pytest
```

### Frontend Tests (Vitest)
```bash
docker-compose run frontend npm run test -- --run
```

## Project Structure
- `backend/`: FastAPI application.
    - `alembic/`: Database migration scripts.
    - `app/models/`: SQLAlchemy database models.
    - `app/api/`: API route handlers.
- `frontend/`: Vite + React + TypeScript + Tailwind v4.
- `e2e/`: Playwright end-to-end tests.
- `docker-compose.yml`: Local development orchestration.
