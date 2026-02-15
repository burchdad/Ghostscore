"""
Database connection and session management
Uses SQLAlchemy with SQLite for family use
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models.db_models import Base

# Database URL - defaults to SQLite for zero-setup
# Can switch to PostgreSQL by setting DATABASE_URL env var
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ghostscore.db"
)

# SQLite-specific options
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False, "timeout": 30}

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency for FastAPI to get database session
    Usage: def my_endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all tables in database
    Call this once on startup
    """
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def reset_db():
    """
    Drop and recreate all tables (development only)
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✓ Database reset")
