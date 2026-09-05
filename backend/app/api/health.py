from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db
from app.schemas.health import HealthResponse
from app.ml.predictor import ml_service
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """
    System Health Check Endpoint.
    Verifies API status, database connectivity, and current active ML mode (DEMO vs REAL).
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    ml_mode = ml_service.get_ml_mode()

    return HealthResponse(
        status="ok",
        database=db_status,
        ml_mode=ml_mode,
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV
    )

@router.get("/model-status")
@router.get("/model/status")
def get_model_status():
    """
    Multi-Crop Model Health & Status Endpoint.
    Exposes loaded model versions, registered crop models, active mode, and threshold policy.
    """
    ml_mode = ml_service.get_ml_mode()
    real_available = ml_service.real_model_available
    registered_models = ml_service.get_registered_models()

    return {
        "status": "active" if real_available else "fallback_demo",
        "ml_mode": ml_mode,
        "model_version": "tomato-v1",
        "architecture": "mobilenet_v3_small",
        "class_count": 4,
        "active_crops": ["tomato", "potato"],
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "models": {
            "tomato": {
                "model_version": "tomato-v1",
                "architecture": "mobilenet_v3_small",
                "class_count": 4,
                "classes": ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"],
                "status": registered_models["tomato"]["status"],
                "provider_type": registered_models["tomato"]["provider_type"]
            },
            "potato": {
                "model_version": "potato-v1",
                "architecture": "mobilenet_v3_small",
                "class_count": 3,
                "classes": ["Potato_Healthy", "Potato_Early_Blight", "Potato_Late_Blight"],
                "status": registered_models["potato"]["status"],
                "provider_type": registered_models["potato"]["provider_type"]
            }
        }
    }
