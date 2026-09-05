from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class ImageQualityResult(BaseModel):
    is_valid: bool
    is_blur_detected: bool
    is_exposure_issue: bool
    blur_score: float
    brightness_score: float
    width: int
    height: int
    quality_message: str

class TopPredictionItem(BaseModel):
    class_name: str = Field(..., alias="class")
    confidence: float

    model_config = ConfigDict(populate_by_name=True)

class PredictionDetailResponse(BaseModel):
    id: str
    predicted_class: str
    confidence: float
    top_predictions: List[Dict[str, Any]]
    model_version: str
    inference_time_ms: float
    is_demo_mode: bool

class ImageMetadataResponse(BaseModel):
    id: str
    file_name: str
    width: Optional[int] = None
    height: Optional[int] = None

class EscalationSummaryResponse(BaseModel):
    is_escalated: bool
    reason: Optional[str] = None
    status: str

class ObservationCreateResponse(BaseModel):
    observation_id: str
    status: str
    crop: str
    crop_stage: str
    submitted_at: datetime
    image: ImageMetadataResponse
    quality_analysis: ImageQualityResult
    prediction: PredictionDetailResponse
    escalation: EscalationSummaryResponse

class ObservationListItem(BaseModel):
    id: str
    crop_id: str
    crop_display_name: str
    crop_stage: str
    symptoms: List[str] = Field(default_factory=list)
    location_village: Optional[str] = "Unknown"
    location_district: Optional[str] = "Unknown"
    location_state: Optional[str] = "Tamil Nadu"
    risk_level: Optional[str] = "MEDIUM"
    status: str
    submitted_at: datetime
    predicted_class: Optional[str] = None
    confidence: Optional[float] = None

class ManualEscalateRequest(BaseModel):
    reason_notes: Optional[str] = Field(None, description="Optional farmer explanation for escalating case.")

class ManualEscalateResponse(BaseModel):
    observation_id: str
    escalation_id: str
    status: str
    reason: str
    message: str
