from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TrustedSource(BaseModel):
    source_id: str
    source_name: str
    domain: str
    authority_tier: int = Field(..., ge=1, le=3, description="Tier 1 (ICAR/TNAU/FAO/EPPO/PPQS), Tier 2 (CABI/Univ/IIHR), Tier 3 (Other Extension)")
    authority_description: str
    enabled: bool = True
    allowed: bool = True
    weight: float = 1.0

class RetrievedEvidence(BaseModel):
    source_id: str = "custom"
    source_name: str
    domain: str
    title: str
    url: str
    evidence_text: str
    authority_tier: int
    crop_relevance: float = 0.0
    disease_relevance: float = 0.0
    symptom_relevance: float = 0.0
    relevance_score: float = 0.0
    retrieved_at: str = ""
    is_cached: bool = False

class ExtractedFact(BaseModel):
    fact_type: str = Field(..., description="'symptoms', 'management', 'prevention', 'monitoring'")
    content: str
    source_name: str
    source_url: str

class AIReviewOutput(BaseModel):
    observation_summary: str
    primary_candidate: str
    alternative_possibilities: List[str] = Field(default_factory=list)
    visible_symptoms: List[str] = Field(default_factory=list)
    evidence_match_summary: str
    severity_estimate: str = "moderate"
    recommended_immediate_actions: List[str] = Field(default_factory=list)
    prevention_monitoring: List[str] = Field(default_factory=list)
    what_to_watch_next: List[str] = Field(default_factory=list)
    vision_confidence: float
    evidence_confidence: float
    overall_confidence: float
    evidence_is_mixed: bool = False
    conflict_notes: Optional[str] = None
    escalation_recommended: bool = False
    sources_used: List[RetrievedEvidence] = Field(default_factory=list)
