import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings, BASE_DIR

logger = logging.getLogger(__name__)

sqlite_fallback_url = f"sqlite:///{BASE_DIR}/hortisentry.db"

def create_resilient_engine():
    primary_url = settings.DATABASE_URL
    if primary_url.startswith("sqlite"):
        return create_engine(
            primary_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG
        )

    # Remote database configured (e.g. Supabase PostgreSQL)
    try:
        eng = create_engine(
            primary_url,
            connect_args={"connect_timeout": 3},
            echo=settings.DEBUG,
            pool_pre_ping=True
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to primary remote database (PostgreSQL/Supabase) successfully.")
        return eng
    except Exception as exc:
        logger.warning(
            f"Unable to connect to primary remote database ({exc}). "
            f"Supabase project may be paused or offline. Automatically falling back to local SQLite: {sqlite_fallback_url}"
        )
        fallback_eng = create_engine(
            sqlite_fallback_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG
        )
        return fallback_eng

engine = create_resilient_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

