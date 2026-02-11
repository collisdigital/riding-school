# Riding School Progress Tracker

A production-grade multi-tenant SaaS platform for tracking rider progress through various grades.

## Core Features
- **Multi-tenancy**: Secure isolation between different riding schools.
- **Onboarding**: Self-service registration and school creation.
- **Rider Management**: Track riders and their achievements per school.
- **Auth**: JWT-based authentication with role-based access control.

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the App
1. Clone the repository.
2. Run `docker-compose up --build`.
3. Open [http://localhost:5173](http://localhost:5173) to see the landing page.
4. Access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

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
docker-compose run -e PYTHONPATH=. backend pytest
```

### Frontend Tests (Vitest)
```bash
docker-compose run frontend npm run test -- --run
```

## Project Structure
- `backend/`: FastAPI application.
- `frontend/`: Vite + React + TypeScript + Tailwind v4.
- `e2e/`: Playwright end-to-end tests.
- `docker-compose.yml`: Local development orchestration.
