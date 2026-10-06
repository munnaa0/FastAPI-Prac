from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent

# "sqlite:///" followed by the full path to the database file.
SQLALCHEMY_DATABASE_URL = f"sqlite:///{BASE_DIR / 'blog.db'}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# A "session" is one short conversation with the database.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """Give one request its own session, then close it when the request ends."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()