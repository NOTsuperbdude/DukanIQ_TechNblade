# pyrefly: ignore[missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore[missing-import]
from sqlalchemy.ext.declarative import declarative_base
# pyrefly: ignore[missing-import]
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# For SQLite, add check_same_thread=False
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
