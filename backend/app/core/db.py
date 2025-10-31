"""
Database configuration and session management.
"""
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ignitehealth:ignitehealth@localhost:5432/medrefills"
)

# Create the engine
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency injector for FastAPI to get database sessions.
    Usage: @app.get("/endpoint")
           def endpoint(session: Session = Depends(get_session)):
    """
    with Session(engine) as session:
        yield session

