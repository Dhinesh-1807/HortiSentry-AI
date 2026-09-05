from app.services.crop_service import CropConfigLoader
from app.core.config import settings

def test_app_settings_loaded():
    """Verify application core settings load correctly."""
    assert settings.APP_NAME is not None
    assert settings.CONFIDENCE_THRESHOLD == 0.70
    assert settings.ML_MODE == "DEMO"

def test_crop_config_loader():
    """Verify crop configuration loader correctly loads dynamic config/crops.yaml."""
    crops = CropConfigLoader.get_supported_crops()
    assert len(crops) > 0
    tomato = next((c for c in crops if c["key"] == "tomato"), None)
    assert tomato is not None
    assert tomato["display_name"] == "Tomato"
    assert len(tomato["stages"]) == 5
    assert len(tomato["disease_classes"]) == 4
    assert "Yellow spots" in tomato["symptoms"]
