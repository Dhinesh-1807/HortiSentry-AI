import logging
from typing import Dict, Any
from fastapi import APIRouter
from app.ml.predictor import ml_service
from app.evidence.source_registry import TrustedSourceRegistry
from app.evidence.retrieval import EvidenceRetrievalService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/vision/status", response_model=Dict[str, Any])
def get_vision_status():
    """Returns the operational status of vision providers and real ML mode availability."""
    ml_mode = ml_service.get_ml_mode()
    return {
        "ml_mode": ml_mode,
        "tomato_model_version": "tomato-v1",
        "tomato_pytorch_available": ml_service.real_model_available,
        "multi_crop_vision_provider": "VisualSymptomAnalyzerProvider",
        "default_mode": "REAL" if ml_service.real_model_available else "DEMO"
    }

@router.get("/evidence/status", response_model=Dict[str, Any])
def get_evidence_status():
    """Returns the operational status of the AI Evidence Engine, trusted sources, and cache stats."""
    sources = TrustedSourceRegistry.get_all_sources()
    cache_stats = EvidenceRetrievalService.get_cache_stats()

    tier1_count = len([s for s in sources if s.authority_tier == 1])
    tier2_count = len([s for s in sources if s.authority_tier == 2])
    tier3_count = len([s for s in sources if s.authority_tier == 3])

    return {
        "evidence_engine_status": "OPERATIONAL",
        "trusted_sources_total": len(sources),
        "tier1_sources_count": tier1_count,
        "tier2_sources_count": tier2_count,
        "tier3_sources_count": tier3_count,
        "cache_stats": cache_stats
    }
