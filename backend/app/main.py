from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from .api import auth, relationships, riders, schools
from .core.config import settings
from .core.seed import seed_rbac
from .db import Base, SessionLocal, engine, get_db

# Import all models to ensure they are registered with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed RBAC
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_rbac(db)
    finally:
        db.close()
    yield
    # Shutdown: Clean up resources if needed


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(schools.router, prefix="/api/schools", tags=["schools"])
app.include_router(riders.router, prefix="/api/riders", tags=["riders"])
app.include_router(
    relationships.router, prefix="/api/relationships", tags=["relationships"]
)


@app.get("/")
def read_root():
    return {"message": "Hello World from Riding School API"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": str(e)},
        )
