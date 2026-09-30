from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL


# SQLite configuration
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def init_db():

    # Import models so SQLAlchemy knows about the tables
    from . import models  # noqa

    Base.metadata.create_all(
        bind=engine
    )


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()