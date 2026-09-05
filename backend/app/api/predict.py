from fastapi import APIRouter, File, UploadFile, Query, HTTPException, status
from PIL import Image
from app.services.media_storage_service import media_storage_service
from app.ml.predictor import ml_service

router = APIRouter(prefix="/predict", tags=["ML Inference Engine"])

@router.post(
    "",
    summary="Direct Image Inference Testing Endpoint",
    description="Submits an image directly to the ML Predictor pipeline to evaluate classification predictions and confidence scores."
)
async def predict_image(
    file: UploadFile = File(..., description="Crop leaf photo"),
    crop: str = Query("tomato", description="Target crop key")
):
    file_bytes = await file.read()
    pil_image = media_storage_service.validate_file(file_bytes, file.filename or "image.jpg")
    
    result = ml_service.predict(pil_image, crop_key=crop)
    return result
