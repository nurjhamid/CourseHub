

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


MYSQL_USER = "root"            
MYSQL_PASSWORD = "root123" 
MYSQL_HOST = "localhost"
MYSQL_DB = "coursehub_db"      


DATABASE_URL = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)


engine = create_engine(
    DATABASE_URL,
    echo=True,    
    future=True,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    """
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    from sqlalchemy import text

    print("Testing DB connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("DB OK, SELECT 1 ->", list(result))
    except Exception as exc:
        print("DB connection FAILED:", exc)
