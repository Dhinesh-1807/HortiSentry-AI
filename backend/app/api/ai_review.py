import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.ai_review_service import AIReviewService

logger = logging.getLogger(__name__)
router = APIRouter()

class AIReviewRequest(BaseModel):
    observation_id: str
    force_refresh: Optional[bool] = False

@router.post("/ai-review", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def generate_ai_review(
    payload: AIReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Generates or retrieves an AI Evidence Review for a given observation.
    Retrieves evidence from trusted agricultural sources and calculates confidence.
    """
    try:
        review_data = AIReviewService.create_or_get_ai_review(
            db=db,
            observation_id=payload.observation_id,
            force_refresh=payload.force_refresh
        )
        return review_data
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Error generating AI review: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate AI review: {str(e)}")

@router.get("/ai-review/{observation_id}", response_model=Dict[str, Any])
def get_ai_review(
    observation_id: str,
    db: Session = Depends(get_db)
):
    """Fetches the latest AI Evidence Review for an observation."""
    review_data = AIReviewService.get_ai_review_by_obs_id(db=db, observation_id=observation_id)
    if not review_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No AI review found for observation '{observation_id}'.")
    return review_data

@router.get("/ai-review/{observation_id}/sources", response_model=List[Dict[str, Any]])
def get_ai_review_sources(
    observation_id: str,
    db: Session = Depends(get_db)
):
    """Fetches verified evidence sources cited in an AI Evidence Review."""
    sources = AIReviewService.get_ai_review_sources(db=db, observation_id=observation_id)
    return sources
