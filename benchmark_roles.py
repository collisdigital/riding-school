import time
import os
import sys

# Add backend to sys.path
sys.path.append(os.getcwd())

from backend.app.db import SessionLocal, engine, Base
from backend.app.models.role import Role
from backend.app.core.seed import seed_rbac

def benchmark():
    # Ensure tables and seed
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_rbac(db)

    # Warm up
    _ = db.query(Role).filter(Role.name == Role.ADMIN).first()

    iterations = 1000
    start = time.time()
    for _ in range(iterations):
        role = db.query(Role).filter(Role.name == Role.ADMIN).first()
        assert role is not None
    end = time.time()

    elapsed = end - start
    print(f"Baseline: {iterations} lookups took {elapsed:.4f}s ({elapsed/iterations*1000:.4f}ms per lookup)")
    db.close()

if __name__ == "__main__":
    benchmark()
