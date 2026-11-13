import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from app.core.config import settings

# Determine database dialect
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
is_postgres = settings.DATABASE_URL.startswith("postgres")

# SQLAlchemy connection arguments and pooling
engine_kwargs = {"echo": False}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    if ":memory:" in settings.DATABASE_URL:
        engine_kwargs["poolclass"] = StaticPool
elif is_postgres or os.getenv("VERCEL"):
    # On serverless (Vercel Functions), use NullPool to prevent connection leakage across cold starts
    engine_kwargs["poolclass"] = NullPool
    # Support connection timeouts
    engine_kwargs["connect_args"] = {"connect_timeout": 10}

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
