import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.expert_service import ExpertService
from app.services.auth_service import get_current_verified_expert
from app.schemas.expert import (
    DashboardStatsResponse, ExpertReviewQueueItem, ExpertReviewDetailResponse,
    CompleteReviewRequest, RequestInfoRequest
)
from app.models.models import ExpertReview, Crop, User

router = APIRouter(
    prefix="/expert",
    tags=["Expert Review Portal"],
    dependencies=[Depends(get_current_verified_expert)]
)

@router.get(
    "/dashboard/stats",
    summary="Get Expert Review Dashboard Key Metrics",
    description="Returns total observations count, pending expert reviews, high-risk cases, reviewed today, and turnaround stats."
)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return ExpertService.get_dashboard_stats(db)

@router.get(
    "/reviews",
    summary="List Expert Review Queue Cases",
    description="Fetches cases pending or under active expert review with filters for status, crop, risk, location."
)
@router.get(
    "/cases",
    summary="List Expert Cases (Alias)",
    description="Alias route for expert cases queue."
)
def list_review_queue(
    status: Optional[str] = Query(None, description="Filter by review status (PENDING, IN_PROGRESS, COMPLETED, NEEDS_INFO)"),
    crop_id: Optional[str] = Query(None, description="Filter by crop ID"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (HIGH, MEDIUM, LOW)"),
    location: Optional[str] = Query(None, description="Filter by district or village name"),
    disease: Optional[str] = Query(None, description="Filter by disease name"),
    observation_id: Optional[str] = Query(None, description="Filter by observation ID"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    reviews = ExpertService.list_review_queue(
        db=db, review_status=status, crop_id=crop_id, risk_level=risk_level, location=location, observation_id=observation_id, limit=limit, offset=offset
    )

    items = []
    for rev in reviews:
        obs = rev.observation
        pred = obs.predictions[0] if obs.predictions else None
        img = obs.images[0] if obs.images else None
        esc = obs.escalations[0] if obs.escalations else None

        items.append({
            "review_id": rev.id,
            "observation_id": obs.id,
            "crop_display_name": obs.crop.display_name if obs.crop else "Unknown",
            "crop_stage": obs.crop_stage,
            "predicted_class": pred.predicted_class if pred else "Unknown",
            "predicted_condition": pred.predicted_condition if pred else "Unknown",
            "confidence": pred.confidence if pred else 0.0,
            "risk_level": obs.risk_level or (pred.risk_level if pred else "MEDIUM"),
            "location": f"{obs.location_village}, {obs.location_district}",
            "escalation_reason": esc.reason if esc else "MANUAL",
            "review_status": rev.review_status,
            "submitted_at": obs.submitted_at,
            "first_symptom_time": obs.first_symptom_time,
            "is_blur_detected": img.is_blur_detected if img else False
        })
    return items

@router.get(
    "/reviews/{review_id}",
    summary="Retrieve Detailed Case for Expert Inspection"
)
@router.get(
    "/cases/{review_id}",
    summary="Retrieve Detailed Case (Alias)"
)
def get_review_detail(
    review_id: str,
    db: Session = Depends(get_db)
):
    rev = ExpertService.get_review_detail(db, review_id)
    obs = rev.observation
    pred = obs.predictions[0] if obs.predictions else None
    img = obs.images[0] if obs.images else None
    esc = obs.escalations[0] if obs.escalations else None
    turnaround = ExpertService.calculate_turnaround_time(obs, rev)

    # Crop display name fallback
    c_name = "Unknown"
    if obs.crop and obs.crop.display_name:
        c_name = obs.crop.display_name
    else:
        c_match = db.query(Crop).filter((Crop.id == obs.crop_id) | (Crop.key == obs.crop_id)).first()
        if c_match and c_match.display_name:
            c_name = c_match.display_name
        elif obs.crop_id:
            c_name = str(obs.crop_id).replace('_', ' ').title()

    # Safely parse symptoms into a list
    symptoms = obs.symptoms
    if isinstance(symptoms, str):
        try:
            parsed = json.loads(symptoms)
            symptoms = parsed if isinstance(parsed, list) else [symptoms]
        except Exception:
            symptoms = [s.strip() for s in symptoms.split(',') if s.strip()]
    elif not isinstance(symptoms, list):
        symptoms = []

    # Safely parse top_predictions into a list
    top_predictions = pred.top_predictions if pred else []
    if isinstance(top_predictions, str):
        try:
            parsed_top = json.loads(top_predictions)
            top_predictions = parsed_top if isinstance(parsed_top, list) else []
        except Exception:
            top_predictions = []
    elif not isinstance(top_predictions, list):
        top_predictions = []

    return {
        "review_id": rev.id,
        "observation_id": obs.id,
        "crop_display_name": c_name,
        "crop_stage": obs.crop_stage or "Not specified",
        "variety": obs.variety,
        "farmer_confidence": obs.farmer_confidence,
        "symptoms": symptoms,
        "location": f"{obs.location_village or 'Local'}, {obs.location_district or 'District'}, {obs.location_state or 'State'}",
        "farmer_notes": obs.notes,
        "symptom_observed_at": obs.symptom_observed_at,
        "first_symptom_time": obs.first_symptom_time,
        "submitted_at": obs.submitted_at,
        "escalation_time": obs.escalation_time,
        "image_url": f"/uploads/{img.file_name}" if (img and img.file_name) else "",
        "risk_level": obs.risk_level or (pred.risk_level if pred else "MEDIUM"),
        "quality_analysis": {
            "is_blur_detected": img.is_blur_detected if img else False,
            "is_exposure_issue": getattr(img, "is_exposure_issue", False) if img else False,
            "blur_score": img.blur_score if img else None,
            "width": img.width if img else None,
            "height": img.height if img else None
        },
        "ai_prediction": {
            "predicted_class": pred.predicted_class if pred else "Unknown",
            "predicted_condition": pred.predicted_condition if pred else "Unknown",
            "confidence": pred.confidence if pred else 0.0,
            "risk_level": pred.risk_level if pred else "MEDIUM",
            "recommended_action": pred.recommended_action if pred else "",
            "needs_expert_review": pred.needs_expert_review if pred else False,
            "top_predictions": top_predictions,
            "is_demo_mode": pred.is_demo_mode if pred else True
        },
        "escalation_reason": esc.reason if esc else "MANUAL",
        "review_status": rev.review_status,
        "expert_prediction": rev.expert_prediction,
        "final_condition": rev.final_condition,
        "expert_assessment": rev.expert_assessment,
        "severity": rev.severity,
        "recommendation": rev.recommendation,
        "follow_up_required": rev.follow_up_required,
        "expert_notes": rev.expert_notes,
        "info_requested_note": rev.info_requested_note,
        "started_at": rev.started_at,
        "completed_at": rev.completed_at,
        "turnaround_metrics": turnaround
    }

@router.post(
    "/reviews/{review_id}/complete",
    summary="Submit Authoritative Expert Diagnosis & Advice"
)
@router.post(
    "/cases/{review_id}/complete",
    summary="Submit Authoritative Expert Diagnosis & Advice (Alias)"
)
@router.post(
    "/cases/{review_id}/review",
    summary="Submit Expert Review (Alias)"
)
def complete_review(
    review_id: str,
    payload: CompleteReviewRequest,
    expert_id: Optional[str] = Query(None, description="Optional expert user ID"),
    current_expert: User = Depends(get_current_verified_expert),
    db: Session = Depends(get_db)
):
    actual_expert_id = expert_id or current_expert.id
    rev = ExpertService.complete_review(
        db=db,
        review_id=review_id,
        expert_prediction=payload.expert_prediction or payload.final_condition or "Healthy",
        final_condition=payload.final_condition or payload.expert_prediction,
        expert_assessment=payload.expert_assessment or payload.expert_notes,
        severity=payload.severity or "MODERATE",
        recommendation=payload.recommendation or payload.expert_notes,
        follow_up_required=payload.follow_up_required or False,
        expert_notes=payload.expert_notes,
        expert_id=actual_expert_id
    )

    return {
        "review_id": rev.id,
        "observation_id": rev.observation_id,
        "review_status": rev.review_status,
        "expert_prediction": rev.expert_prediction,
        "final_condition": rev.final_condition,
        "expert_assessment": rev.expert_assessment,
        "severity": rev.severity,
        "recommendation": rev.recommendation,
        "completed_at": rev.completed_at,
        "message": "Expert review successfully completed and recorded."
    }

@router.post(
    "/reviews/{review_id}/request-info",
    summary="Request Additional Information from Farmer"
)
@router.post(
    "/cases/{review_id}/request-info",
    summary="Request Additional Info (Alias)"
)
def request_more_info(
    review_id: str,
    payload: RequestInfoRequest,
    expert_id: Optional[str] = Query(None, description="Optional expert user ID"),
    current_expert: User = Depends(get_current_verified_expert),
    db: Session = Depends(get_db)
):
    actual_expert_id = expert_id or current_expert.id
    rev = ExpertService.request_more_info(
        db=db,
        review_id=review_id,
        info_note=payload.info_note,
        expert_id=actual_expert_id
    )

    return {
        "review_id": rev.id,
        "observation_id": rev.observation_id,
        "review_status": rev.review_status,
        "info_requested_note": rev.info_requested_note,
        "message": "Information request recorded for farmer notification."
    }

@router.get(
    "/reviewed",
    summary="List Completed / Historical Expert Reviews"
)
def list_reviewed_cases(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    reviews = db.query(ExpertReview).filter(
        ExpertReview.review_status == "COMPLETED"
    ).order_by(ExpertReview.completed_at.desc()).offset(offset).limit(limit).all()

    items = []
    for rev in reviews:
        obs = rev.observation
        items.append({
            "review_id": rev.id,
            "observation_id": obs.id,
            "crop_display_name": obs.crop.display_name if obs.crop else "Unknown",
            "expert_prediction": rev.expert_prediction,
            "final_condition": rev.final_condition,
            "severity": rev.severity,
            "recommendation": rev.recommendation,
            "completed_at": rev.completed_at.isoformat() if rev.completed_at else None,
            "location": f"{obs.location_village}, {obs.location_district}"
        })
    return items
