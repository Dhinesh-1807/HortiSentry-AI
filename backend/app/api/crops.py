from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.crop_service import CropConfigLoader
from app.schemas.crops import CropConfigResponse

router = APIRouter(prefix="/crops", tags=["Crop Configuration"])

@router.get(
    "",
    response_model=List[CropConfigResponse],
    summary="Retrieve Supported Horticultural Crops & Symptom Configurations",
    description="Fetches active dynamic crop configurations with category filters and search queries."
)
def get_supported_crops(
    category: Optional[str] = Query(None, description="Filter crops by category ('vegetables', 'fruits', 'spices_plantation', or 'all')"),
    search: Optional[str] = Query(None, description="Search query for crop name in English or Tamil"),
    db: Session = Depends(get_db)
):
    crops = CropConfigLoader.get_supported_crops(category=category, search_query=search)
    response = []
    for c in crops:
        response.append(CropConfigResponse(
            key=c["key"],
            common_name=c["common_name"],
            display_name=c["display_name"],
            display_name_en=c["display_name_en"],
            display_name_ta=c["display_name_ta"],
            scientific_name=c["scientific_name"],
            category=c["category"],
            supported_status=c["supported_status"],
            disease_knowledge_status=c["disease_knowledge_status"],
            vision_support_status=c["vision_support_status"],
            model_id=c.get("model_id"),
            description=c.get("description", ""),
            stages=c.get("stages", []),
            symptoms=c.get("symptoms", []),
            disease_classes=c.get("disease_classes", [])
        ))
    return response

@router.get(
    "/{crop_id}",
    response_model=CropConfigResponse,
    summary="Retrieve Specific Crop Detail by Crop ID",
    description="Fetches full details and symptom/disease configuration for a single crop."
)
def get_crop_detail(crop_id: str):
    crop_data = CropConfigLoader.get_crop_details(crop_id)
    if not crop_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crop with ID '{crop_id}' not found.")

    return CropConfigResponse(
        key=crop_data["key"],
        common_name=crop_data.get("common_name", crop_id.capitalize()),
        display_name=crop_data.get("display_name", crop_id.capitalize()),
        display_name_en=crop_data.get("display_name_en", crop_id.capitalize()),
        display_name_ta=crop_data.get("display_name_ta", ""),
        scientific_name=crop_data.get("scientific_name", ""),
        category=crop_data.get("category", "vegetables"),
        supported_status=crop_data.get("supported_status", "active"),
        disease_knowledge_status=crop_data.get("disease_knowledge_status", "verified"),
        vision_support_status=crop_data.get("vision_support_status", "knowledge_review"),
        model_id=crop_data.get("model_id"),
        description=crop_data.get("description", ""),
        stages=crop_data.get("stages", []),
        symptoms=crop_data.get("symptoms", []),
        disease_classes=crop_data.get("disease_classes", [])
    )
