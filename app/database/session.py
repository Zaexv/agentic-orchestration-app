"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pathlib import Path

from app.config.settings import settings
from app.database.models import Base


# Determine database URL
if hasattr(settings, 'database_url') and settings.database_url:
    DATABASE_URL = settings.database_url
else:
    # Default to SQLite in data/database/
    db_path = Path(__file__).parent.parent.parent / "data" / "database"
    db_path.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{db_path / 'conversations.db'}"


# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
