import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


DEFAULT_DB = Path(__file__).resolve().parents[1] / "puzzlemint.db"
DATABASE_URL = os.environ.get("PUZZLEMINT_DATABASE_URL", f"sqlite:///{DEFAULT_DB.as_posix()}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})


@event.listens_for(engine, "connect")
def enable_foreign_keys(connection, _record):
    if DATABASE_URL.startswith("sqlite"):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    with SessionLocal() as session:
        yield session
