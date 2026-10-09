from typing import Generator

from sqlalchemy.orm import Session

from packages.shared.config import Settings, get_settings
from packages.shared.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_settings_dep() -> Settings:
    return get_settings()
