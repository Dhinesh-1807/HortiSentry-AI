import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "HortiSentry — AI-Powered Horticultural Disease Observation and Expert Escalation System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/hortisentry.db"
    
    # Configuration Path
    CROP_CONFIG_PATH: str = str(BASE_DIR / "config" / "crops.yaml")
    
    # ML & Decision Engine Configuration
    ML_MODE: str = "DEMO"
    CONFIDENCE_THRESHOLD: float = 0.70
    MODEL_PATH: str = str(BASE_DIR / "ml" / "artifacts" / "tomato_v1.pt")
    POTATO_MODEL_PATH: str = str(BASE_DIR / "ml" / "artifacts" / "potato_v1.pt")
    
    # Image Quality Thresholds (Configurable Heuristics)
    BLUR_THRESHOLD: float = 50.0
    MIN_BRIGHTNESS: float = 30.0
    MAX_BRIGHTNESS: float = 225.0
    MIN_IMAGE_DIMENSION: int = 100
    
    # Storage & Upload Security Configuration
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    ALLOWED_IMAGE_EXTENSIONS: list[str] = ["jpg", "jpeg", "png", "webp"]
    
    # CORS Security
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ]

    model_config = SettingsConfigDict(
        env_file=[str(BASE_DIR / ".env"), str(BASE_DIR / "backend" / ".env")],
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
