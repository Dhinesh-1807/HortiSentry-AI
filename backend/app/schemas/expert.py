from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DashboardStatsResponse(BaseModel):
    total_observations: int
    pending_reviews: int
    low_confidence_cases: int
    completed_reviews: int
    total_escalations: int

class ExpertReviewQueueItem(BaseModel):
    review_id: str
    observation_id: str
    crop_display_name: str
    predicted_class: str
    confidence: float
    escalation_reason: str
    review_status: str
    submitted_at: datetime
    is_blur_detected: bool

class ExpertReviewDetailResponse(BaseModel):
    review_id: str
    observation_id: str
    crop_display_name: str
    crop_stage: str
    symptoms: List[str]
    location: str
    farmer_notes: Optional[str] = None
    symptom_observed_at: Optional[datetime] = None
    submitted_at: datetime
    image_url: str
    quality_analysis: Dict[str, Any]
    ai_prediction: Dict[str, Any]
    escalation_reason: str
    review_status: str
    expert_prediction: Optional[str] = None
    expert_notes: Optional[str] = None
    info_requested_note: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    turnaround_metrics: Optional[Dict[str, Any]] = None

class CompleteReviewRequest(BaseModel):
    expert_prediction: Optional[str] = Field(None, description="Authoritative expert disease prediction")
    final_condition: Optional[str] = Field(None, description="Final condition diagnosis")
    expert_assessment: Optional[str] = Field(None, description="Detailed assessment from expert")
    severity: Optional[str] = Field("MODERATE", description="Severity level: LOW, MODERATE, HIGH, CRITICAL")
    recommendation: Optional[str] = Field(None, description="Actionable recommendation for farmer")
    follow_up_required: Optional[bool] = Field(False, description="Flag if follow-up visit/photo is required")
    expert_notes: Optional[str] = Field(None, description="Guidance notes for the farmer")

class RequestInfoRequest(BaseModel):
    info_note: str = Field(..., description="Description of additional information required from farmer")
