"""
Database engine, session, and declarative base.

All model files import `Base` from here and register themselves on
`Base.metadata` -- that's what Alembic's autogenerate reads to build
migrations, and what tests use to create tables.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://sutms:sutms@localhost:5432/sutms"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
