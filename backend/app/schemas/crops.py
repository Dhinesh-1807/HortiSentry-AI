from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel

class GrowthStageSchema(BaseModel):
    key: str
    display_name: str
    description: Optional[str] = None

class DiseaseClassSchema(BaseModel):
    key: str
    display_name: str
    scientific_name: Optional[str] = None
    severity: Optional[str] = "moderate"
    description: Optional[str] = None

class CropConfigResponse(BaseModel):
    key: str
    common_name: str
    display_name: Optional[str] = None
    display_name_en: Optional[str] = None
    display_name_ta: Optional[str] = None
    scientific_name: Optional[str] = None
    category: str
    supported_status: str = "active"
    disease_knowledge_status: str = "verified"
    vision_support_status: str = "knowledge_review"
    model_id: Optional[str] = None
    description: Optional[str] = None
    stages: List[GrowthStageSchema]
    symptoms: List[Union[Dict[str, Any], str]]
    disease_classes: List[DiseaseClassSchema]
