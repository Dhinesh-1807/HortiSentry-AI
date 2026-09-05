import pytest
from PIL import Image
from app.services.image_quality_service import ImageQualityService
from app.services.media_storage_service import LocalMediaStorageService
from tests.conftest import create_synthetic_image_bytes

def test_image_quality_sharp_image():
    # Sharp image with grid lines
    image_bytes = create_synthetic_image_bytes(format_name="JPEG", size=(400, 400), add_sharp_pattern=True)
    pil_img = Image.open(pytest.importorskip("io").BytesIO(image_bytes))
    
    result = ImageQualityService.analyze_quality(pil_img)
    assert result["is_valid"] is True
    assert result["is_blur_detected"] is False
    assert result["blur_score"] > 50.0

def test_image_quality_too_dark():
    # Solid black image
    image_bytes = create_synthetic_image_bytes(format_name="JPEG", color=(5, 5, 5), size=(300, 300), add_sharp_pattern=False)
    pil_img = Image.open(pytest.importorskip("io").BytesIO(image_bytes))
    
    result = ImageQualityService.analyze_quality(pil_img)
    assert result["is_exposure_issue"] is True
    assert result["brightness_score"] < 30.0

def test_media_storage_unsupported_file():
    storage = LocalMediaStorageService()
    invalid_bytes = b"fake binary exe data"
    
    with pytest.raises(Exception):
        storage.validate_file(invalid_bytes, "malicious.exe")
