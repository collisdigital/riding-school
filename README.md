# Riding School Progress Tracker

A production-grade monorepo for tracking rider progress through various grades.

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the App
1. Clone the repository.
2. Run `docker-compose up --build`.
3. Open [http://localhost:5173](http://localhost:5173) to see the frontend.
4. Access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### Running Tests (Docker - Recommended)
The most reliable way to run tests is via Docker to match the production/development environment.

#### Backend Tests
```bash
docker-compose run -e PYTHONPATH=. backend pytest
```

#### Frontend Tests
```bash
docker-compose run frontend npm run test -- --run
```

### Running Tests (Local)
If you have the dependencies installed locally:

#### Backend
```bash
cd backend
pip install -r requirements.txt
export PYTHONPATH=.
pytest
```

#### Frontend
```bash
cd frontend
npm install
npm run test
```

## Project Structure
- `backend/`: FastAPI application.
- `frontend/`: Vite + React + TypeScript application.
- `docker-compose.yml`: Local development orchestration.
