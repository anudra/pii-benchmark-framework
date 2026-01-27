import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

# Database file path
DATABASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'evaluations.db')}"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

