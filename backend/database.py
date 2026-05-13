from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================
# Phase 2: Persistence & Data Tier Migration
# ==========================================

# 1. Engine Creation (SQLite for local dev, perfectly scalable for later Postgres swap)
SQLALCHEMY_DATABASE_URL = "sqlite:///./meditrace.db"

# connect_args={"check_same_thread": False} is required only for SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2. Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Declarative Base
Base = declarative_base()

# 4. Dependency for FastAPI Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()