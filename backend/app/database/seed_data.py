import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import Crop, ModelVersion, User, Observation, Prediction, Escalation, ExpertReview, Notification, ObservationImage
from app.core.security import hash_password
from app.core.constants import UserRole, ObservationStatus, EscalationStatus, EscalationReason, ReviewStatus, VerificationStatus, AccountStatus

logger = logging.getLogger(__name__)

CROPS_DATA = [
    {"key": "tomato", "display_name": "Tomato", "description": "Solanum lycopersicum — Warm season vegetable crop"},
    {"key": "chilli", "display_name": "Chilli", "description": "Capsicum annuum — Spices and condiments crop"},
    {"key": "brinjal", "display_name": "Brinjal", "description": "Solanum melongena — Eggplant / aubergine crop"},
    {"key": "okra", "display_name": "Okra", "description": "Abelmoschus esculentus — Lady's finger vegetable crop"},
    {"key": "potato", "display_name": "Potato", "description": "Solanum tuberosum — Major tuber vegetable crop"},
    {"key": "cucumber", "display_name": "Cucumber", "description": "Cucumis sativus — Cucurbitaceous fruit vegetable"},
    {"key": "grape", "display_name": "Grape", "description": "Vitis vinifera — High-value temperate & sub-tropical berry crop"},
    {"key": "mango", "display_name": "Mango", "description": "Mangifera indica — King of fruits, perennial horticulture tree"},
    {"key": "banana", "display_name": "Banana", "description": "Musa acuminata — High biomass perennial monocot fruit"},
    {"key": "papaya", "display_name": "Papaya", "description": "Carica papaya — Fast bearing herbaceous tropical fruit"}
]

def seed_initial_data(db: Session):
    """
    Seed initial configuration, demo accounts, and sample observations into the database.
    """
    # 1. Seed Supported Crops
    for c_data in CROPS_DATA:
        crop = db.query(Crop).filter(Crop.key == c_data["key"]).first()
        if not crop:
            crop = Crop(
                key=c_data["key"],
                display_name=c_data["display_name"],
                description=c_data["description"],
                is_active=True
            )
            db.add(crop)

    # 2. Seed Default Model Versions
    for m_ver, arch in [("tomato-v1", "MobileNetV3"), ("potato-v1", "MobileNetV3")]:
        model_ver = db.query(ModelVersion).filter(ModelVersion.version_name == m_ver).first()
        if not model_ver:
            model_ver = ModelVersion(
                version_name=m_ver,
                model_architecture=arch,
                is_active=True
            )
            db.add(model_ver)

    # 3. Seed Standard Demo Accounts (Matching Sections 4, 39)
    demo_farmer = db.query(User).filter(User.email == "farmer@hortisentry.demo").first()
    if not demo_farmer:
        demo_farmer = User(
            name="Ramesh Patel (Demo Farmer)",
            email="farmer@hortisentry.demo",
            password_hash=hash_password("farmer123"),
            role=UserRole.FARMER,
            farmer_code="HS-FARMER-0001",
            phone="+91 98765 43210",
            location="Dharmapuri, Tamil Nadu",
            verification_status=VerificationStatus.NOT_REQUIRED,
            account_status=AccountStatus.ACTIVE,
            is_active=True
        )
        db.add(demo_farmer)
        logger.info("Seeded Demo Farmer account (farmer@hortisentry.demo)")
    else:
        if not demo_farmer.password_hash:
            demo_farmer.password_hash = hash_password("farmer123")
        demo_farmer.verification_status = VerificationStatus.NOT_REQUIRED
        demo_farmer.account_status = AccountStatus.ACTIVE

    demo_expert = db.query(User).filter(User.email == "expert@hortisentry.demo").first()
    if not demo_expert:
        demo_expert = User(
            name="Dr. Ananya Sharma (Lead Horticulturist)",
            email="expert@hortisentry.demo",
            password_hash=hash_password("expert123"),
            role=UserRole.EXPERT,
            phone="+91 98765 43211",
            location="ICAR Horticultural Research Station",
            verification_status=VerificationStatus.VERIFIED,
            account_status=AccountStatus.ACTIVE,
            is_active=True
        )
        db.add(demo_expert)
        logger.info("Seeded Demo Expert account (expert@hortisentry.demo)")
    else:
        if not demo_expert.password_hash:
            demo_expert.password_hash = hash_password("expert123")
        demo_expert.verification_status = VerificationStatus.VERIFIED
        demo_expert.account_status = AccountStatus.ACTIVE

    demo_admin = db.query(User).filter(User.email == "admin@hortisentry.demo").first()
    if not demo_admin:
        demo_admin = User(
            name="Suresh Kumar (Cooperative Manager)",
            email="admin@hortisentry.demo",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            phone="+91 98765 43212",
            location="Regional Cooperative Federation",
            verification_status=VerificationStatus.NOT_REQUIRED,
            account_status=AccountStatus.ACTIVE,
            is_active=True
        )
        db.add(demo_admin)
        logger.info("Seeded Demo Admin account (admin@hortisentry.demo)")
    else:
        if not demo_admin.password_hash:
            demo_admin.password_hash = hash_password("admin123")
        demo_admin.verification_status = VerificationStatus.NOT_REQUIRED
        demo_admin.account_status = AccountStatus.ACTIVE

    # Legacy accounts backwards compatibility
    expert_legacy = db.query(User).filter(User.email == "expert@hortisentry.org").first()
    if not expert_legacy:
        expert_legacy = User(
            name="Dr. Agricultural Expert",
            email="expert@hortisentry.org",
            role="EXPERT",
            password_hash=hash_password("expert123"),
            verification_status=VerificationStatus.VERIFIED,
            account_status=AccountStatus.ACTIVE
        )
        db.add(expert_legacy)
    else:
        expert_legacy.verification_status = VerificationStatus.VERIFIED
        expert_legacy.account_status = AccountStatus.ACTIVE

    farmer_legacy = db.query(User).filter(User.email == "farmer.dev@hortisentry.org").first()
    if not farmer_legacy:
        farmer_legacy = User(
            name="Farmer Development Account",
            email="farmer.dev@hortisentry.org",
            role="FARMER",
            password_hash=hash_password("farmer123"),
            farmer_code="HS-FARMER-0000",
            verification_status=VerificationStatus.NOT_REQUIRED,
            account_status=AccountStatus.ACTIVE
        )
        db.add(farmer_legacy)
    else:
        farmer_legacy.verification_status = VerificationStatus.NOT_REQUIRED
        farmer_legacy.account_status = AccountStatus.ACTIVE

    db.commit()

    # 4. Seed Rich Demo Observations & Turnaround History if database has fewer than 3 observations
    obs_count = db.query(Observation).count()
    if obs_count < 3:
        now = datetime.utcnow()
        tomato_crop = db.query(Crop).filter(Crop.key == "tomato").first()
        chilli_crop = db.query(Crop).filter(Crop.key == "chilli").first()
        potato_crop = db.query(Crop).filter(Crop.key == "potato").first()

        # Observation 1: Completed & Reviewed (Turnaround = 4.2 hours)
        t_first = now - timedelta(hours=5, minutes=30)
        t_sub = now - timedelta(hours=5)
        t_rev = now - timedelta(hours=1, minutes=18) # 4.2 hours after first symptom
        obs1 = Observation(
            user_id=demo_farmer.id,
            crop_id=tomato_crop.id,
            crop_stage="FRUITING",
            variety="Arka Rakshak",
            farmer_confidence=0.85,
            symptoms=["Dark lesions", "Leaf curling"],
            location_village="Attur",
            location_district="Salem",
            location_state="Tamil Nadu",
            notes="Observed concentric dark rings on lower canopy leaves.",
            symptom_observed_at=t_first,
            first_symptom_time=t_first,
            submitted_at=t_sub,
            ai_analysis_time=t_sub + timedelta(seconds=2),
            escalation_time=t_sub + timedelta(seconds=5),
            resolution_time=t_rev,
            risk_level="MEDIUM",
            status=ObservationStatus.EXPERT_REVIEWED
        )
        db.add(obs1)
        db.flush()

        pred1 = Prediction(
            observation_id=obs1.id,
            predicted_class="Early_Blight",
            predicted_condition="Possible Tomato Early Blight",
            confidence=0.88,
            risk_level="MEDIUM",
            recommended_action="Monitor and consider expert review",
            needs_expert_review=True,
            top_predictions=[{"class": "Early_Blight", "confidence": 0.88}, {"class": "Septoria_Leaf_Spot", "confidence": 0.08}],
            inference_time_ms=28.5,
            is_demo_mode=False,
            created_at=t_sub
        )
        db.add(pred1)

        esc1 = Escalation(
            observation_id=obs1.id,
            reason=EscalationReason.LOW_CONFIDENCE,
            status=EscalationStatus.RESOLVED,
            created_at=t_sub,
            resolved_at=t_rev
        )
        db.add(esc1)

        rev1 = ExpertReview(
            observation_id=obs1.id,
            expert_id=demo_expert.id,
            expert_prediction="Early Blight",
            final_condition="Tomato Early Blight (Alternaria solani)",
            expert_assessment="Classic concentric ring lesions observed on lower leaves. Disease is at early-to-moderate stage.",
            severity="MODERATE",
            recommendation="Prune infected bottom leaves, avoid overhead splash irrigation, and apply copper hydroxide / biocontrol Trichoderma.",
            follow_up_required=False,
            expert_notes="Prune lower leaves, avoid overhead irrigation.",
            review_status=ReviewStatus.COMPLETED,
            started_at=t_sub + timedelta(hours=1),
            completed_at=t_rev,
            review_timestamp=t_rev
        )
        db.add(rev1)

        # Observation 2: High Risk Under Review
        t2_first = now - timedelta(hours=3)
        t2_sub = now - timedelta(hours=2, minutes=45)
        obs2 = Observation(
            user_id=demo_farmer.id,
            crop_id=tomato_crop.id,
            crop_stage="FLOWERING",
            variety="Abhinav",
            farmer_confidence=0.70,
            symptoms=["Water-soaked dark lesions", "White mold underside"],
            location_village="Hosur Rural",
            location_district="Krishnagiri",
            location_state="Tamil Nadu",
            notes="Rapid spreading of dark water-soaked spots during humid weather.",
            symptom_observed_at=t2_first,
            first_symptom_time=t2_first,
            submitted_at=t2_sub,
            ai_analysis_time=t2_sub + timedelta(seconds=2),
            escalation_time=t2_sub + timedelta(seconds=3),
            risk_level="HIGH",
            status=ObservationStatus.UNDER_EXPERT_REVIEW
        )
        db.add(obs2)
        db.flush()

        pred2 = Prediction(
            observation_id=obs2.id,
            predicted_class="Late_Blight",
            predicted_condition="Possible Tomato Late Blight",
            confidence=0.92,
            risk_level="HIGH",
            recommended_action="High-risk condition. Immediate quarantine and expert review required.",
            needs_expert_review=True,
            top_predictions=[{"class": "Late_Blight", "confidence": 0.92}, {"class": "Early_Blight", "confidence": 0.05}],
            inference_time_ms=31.2,
            is_demo_mode=False,
            created_at=t2_sub
        )
        db.add(pred2)

        esc2 = Escalation(
            observation_id=obs2.id,
            reason=EscalationReason.HIGH_RISK_CONDITION,
            status=EscalationStatus.UNDER_REVIEW,
            created_at=t2_sub
        )
        db.add(esc2)

        rev2 = ExpertReview(
            observation_id=obs2.id,
            expert_id=demo_expert.id,
            review_status=ReviewStatus.IN_PROGRESS,
            started_at=now - timedelta(minutes=45)
        )
        db.add(rev2)

        # Observation 3: Healthy Foliage (Normal Observation, No Escalation)
        t3_sub = now - timedelta(hours=6)
        obs3 = Observation(
            user_id=demo_farmer.id,
            crop_id=tomato_crop.id,
            crop_stage="VEGETATIVE",
            variety="Vaishnavi",
            farmer_confidence=0.95,
            symptoms=["Normal green foliage"],
            location_village="Thally",
            location_district="Krishnagiri",
            location_state="Tamil Nadu",
            notes="Routine weekly vigor check.",
            symptom_observed_at=t3_sub,
            first_symptom_time=t3_sub,
            submitted_at=t3_sub,
            ai_analysis_time=t3_sub + timedelta(seconds=1),
            risk_level="LOW",
            status=ObservationStatus.COMPLETED
        )
        db.add(obs3)
        db.flush()

        pred3 = Prediction(
            observation_id=obs3.id,
            predicted_class="Healthy",
            predicted_condition="Possible Healthy Tomato Foliage",
            confidence=0.98,
            risk_level="LOW",
            recommended_action="Foliage appears normal. Continue standard monitoring and maintenance.",
            needs_expert_review=False,
            top_predictions=[{"class": "Healthy", "confidence": 0.98}, {"class": "Early_Blight", "confidence": 0.01}],
            inference_time_ms=25.4,
            is_demo_mode=False,
            created_at=t3_sub
        )
        db.add(pred3)

        # Initial Welcome Notification for Demo Farmer
        notif = Notification(
            user_id=demo_farmer.id,
            title="Welcome to HortiSentry",
            message="Your farmer profile HS-FARMER-0001 is active. Report crop symptoms early for instant AI observations and expert support.",
            status="UNREAD",
            created_at=now
        )
        db.add(notif)

        db.commit()
        logger.info("Seeded realistic historical demo observations and expert reviews.")
