from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from packages.shared.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
