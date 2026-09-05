import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    role = Column(String, nullable=False, default="FARMER") # FARMER, EXPERT, ADMIN
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    farmer_code = Column(String, unique=True, nullable=True, index=True) # e.g. HS-FARMER-0001
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    verification_status = Column(String, default="NOT_REQUIRED") # NOT_REQUIRED, PENDING, VERIFIED, REJECTED, SUSPENDED
    account_status = Column(String, default="ACTIVE") # ACTIVE, SUSPENDED, INACTIVE
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    observations = relationship("Observation", back_populates="user")
    reviews = relationship("ExpertReview", back_populates="expert")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

    @property
    def full_name(self):
        return self.name

class Crop(Base):
    __tablename__ = "crops"

    id = Column(String, primary_key=True, default=generate_uuid)
    key = Column(String, unique=True, nullable=False, index=True) # e.g., 'tomato'
    display_name = Column(String, nullable=False) # e.g., 'Tomato'
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    observations = relationship("Observation", back_populates="crop")

class Observation(Base):
    __tablename__ = "observations"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    crop_id = Column(String, ForeignKey("crops.id"), nullable=False, index=True)
    crop_stage = Column(String, nullable=False) # SEEDLING, VEGETATIVE, FLOWERING, FRUITING, HARVEST
    symptoms = Column(JSON, nullable=False) # List of strings e.g. ["Yellow spots", "Leaf curling"]
    location_village = Column(String, nullable=False)
    location_district = Column(String, nullable=False)
    location_state = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    variety = Column(String, nullable=True)
    farmer_confidence = Column(Float, nullable=True, default=0.7) # 0.0 - 1.0
    symptom_observed_at = Column(DateTime, nullable=True)
    first_symptom_time = Column(DateTime, nullable=True) # Alias / normalized time for KPI
    submitted_at = Column(DateTime, default=datetime.utcnow)
    ai_analysis_time = Column(DateTime, nullable=True)
    escalation_time = Column(DateTime, nullable=True)
    resolution_time = Column(DateTime, nullable=True)
    risk_level = Column(String, default="MEDIUM") # LOW, MEDIUM, HIGH
    status = Column(String, default="SUBMITTED", index=True) # SUBMITTED, PENDING_REVIEW, UNDER_REVIEW, REVIEWED, COMPLETED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="observations")
    crop = relationship("Crop", back_populates="observations")
    images = relationship("ObservationImage", back_populates="observation", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="observation", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="observation", cascade="all, delete-orphan")
    reviews = relationship("ExpertReview", back_populates="observation", cascade="all, delete-orphan")
    ai_reviews = relationship("AIReview", back_populates="observation", cascade="all, delete-orphan")

class ObservationImage(Base):
    __tablename__ = "observation_images"

    id = Column(String, primary_key=True, default=generate_uuid)
    observation_id = Column(String, ForeignKey("observations.id"), nullable=False)
    image_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    is_blur_detected = Column(Boolean, default=False)
    is_exposure_issue = Column(Boolean, default=False)
    blur_score = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    observation = relationship("Observation", back_populates="images")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    version_name = Column(String, unique=True, nullable=False) # e.g. 'tomato-v1'
    model_architecture = Column(String, nullable=False, default="MobileNetV3")
    is_active = Column(Boolean, default=True)
    trained_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="model_version")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    observation_id = Column(String, ForeignKey("observations.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=True)
    model_name = Column(String, default="HortiSentry-MobileNet")
    predicted_class = Column(String, nullable=False) # Healthy, Early Blight, Late Blight, Leaf Spot
    predicted_condition = Column(String, nullable=True) # e.g. "Possible Tomato Early Blight"
    confidence = Column(Float, nullable=False, index=True) # 0.0 - 1.0
    risk_level = Column(String, default="MEDIUM") # LOW, MEDIUM, HIGH
    recommended_action = Column(String, nullable=True) # Guidance action
    needs_expert_review = Column(Boolean, default=False)
    top_predictions = Column(JSON, nullable=False) # List of dicts [{class, confidence}]
    inference_time_ms = Column(Float, default=0.0)
    is_demo_mode = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    observation = relationship("Observation", back_populates="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")

class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(String, primary_key=True, default=generate_uuid)
    observation_id = Column(String, ForeignKey("observations.id"), nullable=False)
    reason = Column(String, nullable=False) # LOW_CONFIDENCE, POOR_IMAGE_QUALITY, MANUAL_FARMER_REQUEST, UNKNOWN_CLASS
    status = Column(String, default="RECOMMENDED", index=True) # RECOMMENDED, SUBMITTED, UNDER_REVIEW, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    observation = relationship("Observation", back_populates="escalations")

class ExpertReview(Base):
    __tablename__ = "expert_reviews"

    id = Column(String, primary_key=True, default=generate_uuid)
    observation_id = Column(String, ForeignKey("observations.id"), nullable=False)
    expert_id = Column(String, ForeignKey("users.id"), nullable=True)
    expert_prediction = Column(String, nullable=True) # Validated or Corrected Class
    final_condition = Column(String, nullable=True) # Normalized final disease diagnosis
    expert_assessment = Column(Text, nullable=True) # Full assessment summary
    severity = Column(String, nullable=True) # LOW, MODERATE, HIGH, CRITICAL
    recommendation = Column(Text, nullable=True) # Farmer recommendation
    follow_up_required = Column(Boolean, default=False)
    expert_notes = Column(Text, nullable=True)
    info_requested_note = Column(Text, nullable=True)
    review_status = Column(String, default="PENDING", index=True) # PENDING, IN_PROGRESS, COMPLETED, NEEDS_INFO
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    review_timestamp = Column(DateTime, nullable=True) # review completion timestamp

    observation = relationship("Observation", back_populates="reviews")
    expert = relationship("User", back_populates="reviews")

class AIReview(Base):
    __tablename__ = "ai_reviews"

    id = Column(String, primary_key=True, default=generate_uuid)
    observation_id = Column(String, ForeignKey("observations.id"), nullable=False, index=True)
    crop_key = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    primary_candidate = Column(String, nullable=False)
    vision_confidence = Column(Float, nullable=False)
    evidence_confidence = Column(Float, nullable=False)
    overall_confidence = Column(Float, nullable=False, index=True)
    severity = Column(String, default="moderate")
    recommended_actions = Column(JSON, nullable=False)
    prevention_monitoring = Column(JSON, nullable=False)
    what_to_watch = Column(JSON, nullable=False)
    evidence_is_mixed = Column(Boolean, default=False)
    conflict_notes = Column(Text, nullable=True)
    is_demo_mode = Column(Boolean, default=False)
    provider_info = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    observation = relationship("Observation", back_populates="ai_reviews")
    evidences = relationship("ReviewEvidence", back_populates="ai_review", cascade="all, delete-orphan")

class ReviewEvidence(Base):
    __tablename__ = "review_evidence"

    id = Column(String, primary_key=True, default=generate_uuid)
    ai_review_id = Column(String, ForeignKey("ai_reviews.id"), nullable=False, index=True)
    source_name = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    evidence_text = Column(Text, nullable=False)
    relevance_score = Column(Float, nullable=False)
    authority_tier = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    ai_review = relationship("AIReview", back_populates="evidences")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    observation_id = Column(String, ForeignKey("observations.id"), nullable=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default="UNREAD", index=True) # UNREAD, READ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="notifications")
    observation = relationship("Observation")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String, nullable=True)
    action = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)

    user = relationship("User", back_populates="audit_logs")

# Explicit composite indexes for high-frequency queries
Index("idx_obs_status_created", Observation.status, Observation.created_at)
Index("idx_review_status_started", ExpertReview.review_status, ExpertReview.started_at)
Index("idx_ai_review_obs_conf", AIReview.observation_id, AIReview.overall_confidence)
Index("idx_notif_user_status", Notification.user_id, Notification.status)
Index("idx_audit_action_time", AuditLog.action, AuditLog.timestamp)
