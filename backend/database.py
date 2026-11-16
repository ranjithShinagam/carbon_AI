from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Always use the carbon_app.db located inside the backend folder
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "carbon_app.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

print("=" * 70)
print("CARBON AI DATABASE")
print(f"Database: {DATABASE_PATH}")
print("=" * 70)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()