import logging
from sqlalchemy import text
from app.database.connection import engine, Base, SessionLocal
from app.database.seed_data import seed_initial_data
import app.models # Register models with Base

logger = logging.getLogger(__name__)

def migrate_missing_columns():
    """
    Safely adds newly declared columns to existing SQLite tables if they do not yet exist.
    """
    from app.core.config import settings
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    migrations = [
        ("users", "password_hash", "TEXT"),
        ("users", "farmer_code", "TEXT"),
        ("users", "phone", "TEXT"),
        ("users", "location", "TEXT"),
        ("users", "verification_status", "TEXT DEFAULT 'NOT_REQUIRED'"),
        ("users", "account_status", "TEXT DEFAULT 'ACTIVE'"),
        ("users", "updated_at", "DATETIME"),
        ("users", "is_active", "BOOLEAN DEFAULT 1"),

        ("observations", "variety", "TEXT"),
        ("observations", "farmer_confidence", "FLOAT DEFAULT 0.7"),
        ("observations", "first_symptom_time", "DATETIME"),
        ("observations", "ai_analysis_time", "DATETIME"),
        ("observations", "escalation_time", "DATETIME"),
        ("observations", "resolution_time", "DATETIME"),
        ("observations", "risk_level", "TEXT DEFAULT 'MEDIUM'"),

        ("predictions", "model_name", "TEXT DEFAULT 'HortiSentry-MobileNet'"),
        ("predictions", "predicted_condition", "TEXT"),
        ("predictions", "risk_level", "TEXT DEFAULT 'MEDIUM'"),
        ("predictions", "recommended_action", "TEXT"),
        ("predictions", "needs_expert_review", "BOOLEAN DEFAULT 0"),

        ("expert_reviews", "final_condition", "TEXT"),
        ("expert_reviews", "expert_assessment", "TEXT"),
        ("expert_reviews", "severity", "TEXT DEFAULT 'MODERATE'"),
        ("expert_reviews", "recommendation", "TEXT"),
        ("expert_reviews", "follow_up_required", "BOOLEAN DEFAULT 0"),
        ("expert_reviews", "review_timestamp", "DATETIME")
    ]

    with engine.connect() as conn:
        for table, col, col_type in migrations:
            try:
                # Check if table exists
                tbl_check = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")).fetchone()
                if not tbl_check:
                    continue
                # Check if column exists
                cols = [row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()]
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                    conn.commit()
                    logger.info(f"Added column '{col}' ({col_type}) to table '{table}'")
            except Exception as e:
                logger.warning(f"Note on migration for {table}.{col}: {e}")

def init_db():
    """
    Initialize SQLite database tables and seed mandatory initial configuration records.
    """
    logger.info("Initializing SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    migrate_missing_columns()
    
    db = SessionLocal()
    try:
        seed_initial_data(db)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
