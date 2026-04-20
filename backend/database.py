from pathlib import Path
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.getenv("NYELVCSERE_DB_PATH", str(BASE_DIR / "nyelvcsere.db"))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{Path(DB_PATH).as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()