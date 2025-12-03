"""
database.py
-----------
Database configuration and session management for CourseHub.

This module is the low-level Model layer responsible for connecting
to the MySQL database and providing SQLAlchemy sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# === Adjust these for your machine ===
MYSQL_USER = "root"            # your MySQL username
MYSQL_PASSWORD = "root123"     # your MySQL password
MYSQL_HOST = "localhost"
MYSQL_DB = "coursehub_db"      # make sure this DB actually exists

# SQLAlchemy connection URL.
# Requires: pip install mysql-connector-python
DATABASE_URL = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,    # set to False when you don’t want SQL logs
    future=True,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session.
    The session is automatically closed at the end of the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Optional: quick manual test if you run this file directly.
if __name__ == "__main__":
    from sqlalchemy import text

    print("Testing DB connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("DB OK, SELECT 1 ->", list(result))
    except Exception as exc:
        print("DB connection FAILED:", exc)
