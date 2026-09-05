import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.observation_service import ObservationService
from app.services.escalation_service import EscalationService
from app.models.models import Crop
from app.schemas.observation import (
    ObservationCreateResponse, ObservationListItem, ManualEscalateRequest, ManualEscalateResponse
)

router = APIRouter(prefix="/observations", tags=["Farmer Observations"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Submit New Horticultural Crop Observation",
    description="Accepts multipart form submission containing crop leaf photo, stage, symptom choices, and coarse location. Executes quality analysis, AI prediction, and automatic escalation engine."
)
async def create_observation(
    crop_id: str = Form(..., description="Crop identifier (e.g., 'tomato')"),
    crop_stage: str = Form(..., description="Growth stage (SEEDLING, VEGETATIVE, FLOWERING, FRUITING, HARVEST)"),
    symptoms: str = Form(..., description="Selected symptoms (JSON array or comma-separated list)"),
    village: str = Form(..., description="Village location"),
    district: str = Form(..., description="District location"),
    state: str = Form(..., description="State location"),
    variety: Optional[str] = Form(None, description="Optional crop variety"),
    farmer_confidence: Optional[float] = Form(0.7, description="Farmer confidence (0.0 to 1.0)"),
    notes: Optional[str] = Form(None, description="Optional farmer notes"),
    symptom_observed_at: Optional[str] = Form(None, description="Optional ISO timestamp when symptoms were first noticed"),
    observation_date: Optional[str] = Form(None, description="Alias for symptom_observed_at"),
    user_id: Optional[str] = Form(None, description="Optional farmer user ID"),
    file: UploadFile = File(..., description="Crop leaf photo file"),
    db: Session = Depends(get_db)
):
    # Parse symptoms
    parsed_symptoms = []
    try:
        if symptoms.startswith("["):
            parsed_symptoms = json.loads(symptoms)
        else:
            parsed_symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symptoms field must be a valid JSON array or comma-separated list of strings."
        )

    # Parse symptom_observed_at timestamp
    raw_date = symptom_observed_at or observation_date
    parsed_observed_at = None
    if raw_date:
        try:
            parsed_observed_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        except ValueError:
            try:
                parsed_observed_at = datetime.strptime(raw_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format for symptom observation date. Use YYYY-MM-DD or ISO timestamp."
                )

    # Read image bytes
    file_bytes = await file.read()

    result = ObservationService.create_observation(
        db=db,
        crop_id=crop_id,
        crop_stage=crop_stage,
        symptoms=parsed_symptoms,
        village=village,
        district=district,
        state=state,
        file_bytes=file_bytes,
        original_filename=file.filename or "observation.jpg",
        notes=notes,
        variety=variety,
        farmer_confidence=farmer_confidence,
        symptom_observed_at=parsed_observed_at,
        user_id=user_id
    )

    return result

@router.get(
    "",
    response_model=List[ObservationListItem],
    summary="List Filtered Observations",
    description="Returns chronological list of observations with optional filters for crop, review status, and pagination."
)
def list_observations(
    crop_id: Optional[str] = Query(None, description="Filter by crop ID"),
    status: Optional[str] = Query(None, description="Filter by observation status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    observations = ObservationService.list_observations(
        db=db, crop_id=crop_id, obs_status=status, limit=limit, offset=offset
    )

    result = []
    for obs in observations:
        pred = obs.predictions[0] if obs.predictions else None
        
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

        # Safely parse symptoms
        symptoms = obs.symptoms or []
        if isinstance(symptoms, str):
            try:
                parsed_s = json.loads(symptoms)
                symptoms = parsed_s if isinstance(parsed_s, list) else [symptoms]
            except Exception:
                symptoms = [s.strip() for s in symptoms.split(',') if s.strip()]
        elif not isinstance(symptoms, list):
            symptoms = []

        result.append({
            "id": obs.id,
            "crop_id": obs.crop_id,
            "crop_display_name": c_name,
            "crop_stage": obs.crop_stage,
            "symptoms": symptoms,
            "location_village": obs.location_village or "Unknown",
            "location_district": obs.location_district or "Unknown",
            "location_state": obs.location_state or "Tamil Nadu",
            "risk_level": obs.risk_level or (pred.risk_level if pred else "MEDIUM"),
            "status": obs.status,
            "submitted_at": obs.submitted_at,
            "predicted_class": pred.predicted_class if pred else None,
            "confidence": pred.confidence if pred else None,
        })

    return result

@router.get(
    "/{observation_id}",
    summary="Get Detailed Observation by ID",
    description="Returns full observation entity with linked image, prediction, escalation, and review status."
)
def get_observation_detail(
    observation_id: str,
    db: Session = Depends(get_db)
):
    obs = ObservationService.get_observation_by_id(db, observation_id)
    img = obs.images[0] if obs.images else None
    pred = obs.predictions[0] if obs.predictions else None
    esc = obs.escalations[0] if obs.escalations else None
    rev = obs.reviews[0] if obs.reviews else None

    # Resolve crop display name safely
    crop_name = None
    if obs.crop and obs.crop.display_name:
        crop_name = obs.crop.display_name
    else:
        crop_match = db.query(Crop).filter((Crop.id == obs.crop_id) | (Crop.key == obs.crop_id)).first()
        if crop_match and crop_match.display_name:
            crop_name = crop_match.display_name
        else:
            crop_name = str(obs.crop_id).replace('_', ' ').title() if obs.crop_id else "Horticultural Crop"

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

    sub_time_str = obs.submitted_at.isoformat() if obs.submitted_at else None
    sym_time_str = obs.symptom_observed_at.isoformat() if obs.symptom_observed_at else None

    return {
        "id": obs.id,
        "crop_id": obs.crop_id,
        "crop_display_name": crop_name,
        "crop_stage": obs.crop_stage or "Not specified",
        "variety": obs.variety,
        "farmer_confidence": obs.farmer_confidence if obs.farmer_confidence is not None else 0.7,
        "risk_level": obs.risk_level or (pred.risk_level if pred else "MEDIUM"),
        "symptoms": symptoms,
        "location": {
            "village": obs.location_village or "Not specified",
            "district": obs.location_district or "Not specified",
            "state": obs.location_state or "Not specified"
        },
        "notes": obs.notes,
        "symptom_observed_at": sym_time_str,
        "first_symptom_time": obs.first_symptom_time.isoformat() if obs.first_symptom_time else None,
        "submitted_at": sub_time_str,
        "timestamps": {
            "symptom_observed_at": sym_time_str,
            "submitted_at": sub_time_str
        },
        "ai_analysis_time": obs.ai_analysis_time.isoformat() if obs.ai_analysis_time else None,
        "escalation_time": obs.escalation_time.isoformat() if obs.escalation_time else None,
        "resolution_time": obs.resolution_time.isoformat() if obs.resolution_time else None,
        "status": obs.status,
        "predicted_class": pred.predicted_class if pred else None,
        "confidence": pred.confidence if pred else None,
        "escalation_reason": esc.reason if esc else None,
        "image": {
            "id": img.id if img else None,
            "file_name": img.file_name if img else None,
            "image_url": f"/uploads/{img.file_name}" if img and img.file_name else None,
            "width": img.width if img else None,
            "height": img.height if img else None,
            "is_blur_detected": img.is_blur_detected if img else False,
            "is_exposure_issue": getattr(img, "is_exposure_issue", False) if img else False,
            "blur_score": img.blur_score if img else None
        },
        "prediction": {
            "id": pred.id if pred else None,
            "predicted_class": pred.predicted_class if pred else "Screening in Progress",
            "predicted_condition": pred.predicted_condition if pred else None,
            "confidence": pred.confidence if pred else 0.0,
            "risk_level": pred.risk_level if pred else "MEDIUM",
            "recommended_action": pred.recommended_action if pred else None,
            "needs_expert_review": pred.needs_expert_review if pred else False,
            "top_predictions": top_predictions,
            "model_version": pred.model_version.version_name if (pred and pred.model_version) else "demo-v1",
            "is_demo_mode": pred.is_demo_mode if pred else True
        },
        "escalation": {
            "is_escalated": esc is not None,
            "reason": esc.reason if esc else None,
            "status": esc.status if esc else "NOT_REQUIRED"
        },
        "expert_review": {
            "status": rev.review_status if rev else "NOT_ESCALATED",
            "expert_prediction": rev.expert_prediction if rev else None,
            "final_condition": rev.final_condition if rev else None,
            "expert_assessment": rev.expert_assessment if rev else None,
            "severity": rev.severity if rev else None,
            "recommendation": rev.recommendation if rev else None,
            "treatment_recommendation": rev.recommendation if rev else None,
            "expert_notes": rev.expert_notes if rev else None,
            "info_requested_note": rev.info_requested_note if rev else None,
            "expert_name": (rev.expert.name or rev.expert.full_name) if (rev and rev.expert) else "Agricultural Specialist",
            "reviewed_at": (rev.completed_at or rev.review_timestamp).isoformat() if (rev and (rev.completed_at or rev.review_timestamp)) else None,
            "completed_at": rev.completed_at.isoformat() if (rev and rev.completed_at) else None
        }
    }

@router.post(
    "/{observation_id}/analyze",
    summary="Re-run AI Analysis on Observation",
    description="Allows requesting a fresh AI inference on an uploaded observation image."
)
def analyze_observation(
    observation_id: str,
    db: Session = Depends(get_db)
):
    return ObservationService.analyze_observation(db, observation_id)

@router.post(
    "/{observation_id}/escalate",
    response_model=ManualEscalateResponse,
    summary="Manually Escalate Observation to Expert Review",
    description="Allows a farmer to manually request human expert review for any observation."
)
def manual_escalate(
    observation_id: str,
    payload: ManualEscalateRequest,
    db: Session = Depends(get_db)
):
    obs = ObservationService.get_observation_by_id(db, observation_id)
    escalation = EscalationService.manual_farmer_escalate(
        db=db, observation=obs, user_notes=payload.reason_notes
    )

    return ManualEscalateResponse(
        observation_id=obs.id,
        escalation_id=escalation.id,
        status=escalation.status,
        reason=escalation.reason,
        message="Observation successfully escalated to human expert queue."
    )
