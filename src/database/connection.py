"""
Database Connection Manager using SQLAlchemy.
Supports SQLite (default) and PostgreSQL / MySQL connection strings.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DEFAULT_DB_PATH = "data/ecommerce.db"

def get_db_url(db_path: str = DEFAULT_DB_PATH) -> str:
    """Returns database URL from environment variable or local SQLite file."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return f"sqlite:///{os.path.abspath(db_path)}"

def get_db_engine(db_path: str = DEFAULT_DB_PATH):
    """Creates and returns SQLAlchemy Engine."""
    url = get_db_url(db_path)
    engine = create_engine(url, echo=False)
    return engine

def get_db_session(db_path: str = DEFAULT_DB_PATH) -> Session:
    """Returns a new SQLAlchemy Session."""
    engine = get_db_engine(db_path)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
