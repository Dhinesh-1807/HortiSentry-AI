# HortiSentry

> **"AI-Assisted Crop Disease Observation & Expert Escalation Platform"**

HortiSentry is a software-only AI-assisted platform designed to help horticulture farmers report crop disease symptoms early using crop images and structured observations. The system performs AI-assisted analysis, provides confidence and risk information, and escalates uncertain or high-risk cases to verified agricultural experts for review.

---

### Core System Principles
- **Software-Only Solution:** 100% web application software. Requires no hardware sensors, IoT nodes, field microcontrollers, or external camera rigs.
- **No Hardware/IoT Components:** Relies exclusively on standard farmer smartphone or web image uploads and structured input forms.
- **Decision-Support Architecture:** AI outputs provide probabilistic condition screening and advisory support, not automated diagnostic certification.
- **Human-in-the-Loop Safeguard:** AI does not replace certified agricultural specialists; cases flagged with low confidence, high disease risk, or poor image quality are routed directly to verified experts.

---

## 1. Project Overview

HortiSentry bridges the critical communication and triage gap between grassroots horticultural farmers and agricultural extension specialists. By integrating lightweight computer vision with structured symptom collection and a multi-tier human review workflow, the platform ensures that potential plant health threats are captured and evaluated early.

- **Farmer Symptom Reporting:** Farmers submit digital observations documenting affected crops, growth stages, visible symptoms, and coarse geographical data.
- **Leaf Imagery Upload:** Farmers capture and upload crop leaf images directly from mobile or desktop web browsers.
- **Structured Context Collection:** Contextual field data (e.g., vegetative/fruiting stage, symptom categories, local weather context) complements visual imagery.
- **AI-Assisted Initial Screening:** On-device/server-side inference delivers an initial possible-condition assessment with associated confidence scores.
- **Risk & Quality Assessment:** Heuristic engines examine image clarity (blur, exposure) and disease virulence to assign a dynamic risk level.
- **Uncertainty & High-Risk Escalation:** Observations falling below confidence thresholds or exhibiting high-risk traits are automatically placed into the expert review queue.
- **Verified Expert Review Portal:** Only administrator-approved agricultural specialists can evaluate escalated cases, inspect high-resolution imagery, and submit binding assessments.
- **Transparent Status Tracking:** Farmers track case progress in real time across a multi-step timeline (Submitted $\rightarrow$ AI Screened $\rightarrow$ Expert Review $\rightarrow$ Resolved).
- **Administrative Governance & Telemetry:** Agricultural cooperative administrators manage user accounts, verify expert credentials, monitor review turnaround SLAs, and audit system activities.

---

## 2. Problem Statement

Horticultural producers face significant challenges when diagnosing and managing crop diseases in field conditions:

1. **Delayed Symptom Reporting:** Farmers often detect disease symptoms only after significant foliage damage has occurred or delay reporting due to lack of accessible local extension officers.
2. **Inconsistent & Unstructured Records:** Phone descriptions or casual chat messages lack consistent visual evidence, growth stage context, and standardization, making remote diagnosis error-prone.
3. **Delayed Expert Review:** Extension specialists are overwhelmed with manual requests, resulting in critical diagnostic bottlenecks.
4. **Fragile Record-Keeping:** Historical disease incidences are rarely logged systematically, hindering regional cooperative tracking.

These systemic delays directly impair:
- **Early Observation:** Inability to detect focal infections before field-wide dissemination.
- **Crop Monitoring:** Inadequate tracking of seasonal disease progression.
- **Quality Management:** Inconsistent inspection standards across disparate farming communities.
- **Expert Response:** Slower specialist response times during peak infection outbreaks.
- **Record Keeping:** Complete lack of auditable historical records for cooperative planning.

*(Note: HortiSentry provides structured decision support to streamline response workflows and does not make unverified claims of guaranteed crop yield preservation.)*

---

## 3. Proposed Solution

HortiSentry implements a closed-loop observation-to-resolution pipeline:

```
[ Farmer ]
   │
   ├─► 1. Captures Crop Leaf Photo & Selects Field Symptoms
   │
   ├─► 2. Submits Structured Observation via Web Interface
   │
[ Backend Processing ]
   │
   ├─► 3. Validates Image Integrity & Heuristic Quality (Blur/Exposure)
   │
   ├─► 4. Executes AI-Assisted Inference (MobileNetV3 PyTorch Engine)
   │
   ├─► 5. Calculates Prediction Confidence & Disease Risk Level
   │
   ├─► 6. Applies Escalation Rules (Configurable Confidence & Risk Policies)
   │
[ Human-in-the-Loop Review ]
   │
   ├─► 7. Routes Uncertain / High-Risk Cases to Verified Expert Queue
   │
   ├─► 8. Verified Agricultural Expert Conducts In-Depth Case Review
   │
   ├─► 9. Expert Submits Authoritative Assessment & Non-Chemical Advice
   │
[ Resolution & Telemetry ]
   │
   ├─► 10. Farmer Receives Real-Time Timeline Notification & Guidance
   │
   └─► 11. Cooperative Admin Monitors Turnaround Metrics & Regional Trends
```

---

## 4. Key Features

### Farmer Features
- **Secure Authentication:** Self-service registration with automatic assignment of a non-identifiable code (`HS-FARMER-XXXX`) and manual login flow.
- **Structured Observation Wizard:** 4-step guided submission workflow covering crop identification, growth stage, visual symptom selection, and coarse location.
- **Crop Image Upload:** Secure photo upload supporting JPEG, PNG, and WebP with client-side preview and image validation.
- **Dynamic Crop Knowledge Catalog:** Dynamic catalog covering 32 horticultural crops across Vegetables, Fruits, and Spices/Plantation with bilingual support (English & Tamil).
- **AI-Assisted Screening:** Immediate feedback displaying the possible condition, confidence percentage, and assigned risk tier.
- **Dual Inference Mode:** Real PyTorch MobileNetV3 model execution with automated fallback to deterministic demo screening.
- **Manual Escalation Option:** Ability for farmers to request human expert review even when AI confidence is high.
- **Observation History & Timeline:** Searchable historical log of all personal submissions with visual progress steppers tracking expert reviews.
- **Notification Inbox:** In-app notification center alerting farmers when expert assessments or info requests are issued.

### Expert Features
- **Strict Verification Gate:** Expert accounts require explicit administrator review and verification before gaining access.
- **Prioritized Review Queue:** Escalated cases organized into actionable queues filtered by urgency (High, Medium, Low risk), crop, and escalation reason.
- **Deep Photo Inspection:** High-resolution zoomable image inspection viewer with automated image quality diagnostic indicators (blur score, exposure check).
- **Comprehensive Case Dossier:** Access to farmer symptoms, field stage, coarse location, AI top-3 prediction probabilities, and turnaround time metrics.
- **Authoritative Review Submission:** Structured forms to record validated condition, severity level, follow-up flags, and non-chemical management recommendations.
- **Information Request Workflow:** Two-way clarification mechanism enabling specialists to request additional photos or symptom updates from the farmer.
- **Reviewed Case History:** Archival log of all historical reviews completed by the expert.

### Admin Features
- **Administrative Telemetry Dashboard:** High-level dashboard showing total users, active observations, pending escalations, and model health.
- **Expert Verification Governance:** Interface to review, approve, reject, or suspend agricultural specialist applications.
- **User Management & Moderation:** Full user roster with ability to inspect activity, toggle account access, or deactivate users.
- **Time-to-Expert KPI Analytics:** Live SLA compliance monitoring measuring elapsed time from symptom observation to expert resolution.
- **Regional & Disease Analytics:** Aggregated distribution metrics across crops, disease classifications, and geographic districts.
- **Model & Dataset Information:** Real-time visibility into active model architectures, test metrics, confusion matrices, and dataset quality audits.
- **Immutable Audit Logging:** System-wide audit trail recording user registrations, logins, expert verifications, and escalations.

---

## 5. How HortiSentry Works

```
Farmer Submits Case ──► Quality Audit (Blur/Exposure)
                                │
                                ▼
                       AI Model Inference
                                │
                                ▼
                  Calculates Confidence & Risk
                                │
          ┌─────────────────────┴─────────────────────┐
          ▼                                           ▼
[ Confidence >= 0.85 & Low Risk ]     [ Confidence < 0.85 OR High Risk ]
          │                                           │
          ▼                                           ▼
   Direct Observation                     Escalates to Review Queue
   (Farmer Advisory)                                  │
                                                      ▼
                                           Verified Expert Reviews
                                                      │
                                                      ▼
                                           Assessment & Resolution
                                                      │
                                                      ▼
                                           Farmer Receives Update
```

1. **Submission:** The farmer submits an image and selects visual symptoms (e.g., yellow spots, curling, dark lesions) and crop stage.
2. **Quality Audit:** The backend inspects the image for blur using Laplacian variance ($\\sigma^2 < 50.0$) and brightness extremes ($< 30.0$ or $> 225.0$).
3. **Inference:** The PyTorch MobileNetV3 engine preprocesses the leaf image ($224 \\times 224$ normalized RGB tensor) and generates class probability distributions.
4. **Risk Evaluation:** The system correlates the predicted class with the virulence database (e.g., Late Blight is categorized as `HIGH` risk, Healthy as `LOW` risk).
5. **Escalation Decision:** If the model confidence is low, the disease is high risk, image quality is suspect, or the farmer manually requests review, an `Escalation` record is created.
6. **Expert Review:** An admin-verified specialist inspects the dossier, adjusts or confirms the diagnosis, and provides actionable advice.
7. **Farmer Notification:** The farmer receives an in-app alert, reviews the specialist's recommendations, and monitors crop recovery.

---

## 6. User Roles

HortiSentry enforces strict Role-Based Access Control (RBAC) across three distinct user roles:

| Role | Access Scope | Portal Destination | Verification Requirement |
| :--- | :--- | :--- | :--- |
| **Farmer** | Submit observations, view personal history, receive review updates | `/farmer` | None (instant access upon registration) |
| **Expert** | Access review queues, inspect escalated leaf photos, submit expert reviews | `/expert` | **Mandatory Admin Verification** (Status must be `VERIFIED`) |
| **Admin** | System telemetry, verify experts, manage users, view analytics & audit logs | `/admin` | Seeded administrative credentials |

---

## 7. Authentication & Authorization

### Registration & Login Separation
- **No Automatic Authentication on Sign-up:** Registering an account creates user credentials in the database but **does not issue a JWT token**.
- **Explicit Login Flow:** Users are redirected to the login page after registration and must enter their credentials manually to authenticate.

```
Register Form ──► Account Created ──► Redirected to Login ──► Enters Credentials ──► Dashboard
```

### Expert Verification Workflow
A user cannot access expert capabilities simply by selecting the "Expert" role during registration:

```
Expert Registers ──► Status: PENDING ──► Admin Verifies ──► Status: VERIFIED ──► Portal Access
```

1. Upon registration with role `EXPERT`, the account is created with `verification_status = "PENDING"` and `is_active = True`.
2. If a pending expert signs in, frontend route guards intercept the session and redirect to `/expert/status`.
3. An Administrator reviews the application in the Admin Portal (`/admin/expert-verifications`) and executes an `APPROVE` or `REJECT` action.
4. Only upon receiving `verification_status = "VERIFIED"` can the expert access `/expert/queue` and case inspection endpoints.

### Backend Authorization Enforcement
Every incoming API request is authorized using dependency injection guards in FastAPI:
- `get_current_user`: Validates JWT signature, expiration, and user account status (`HTTP 401 Unauthorized` if invalid or expired).
- `get_current_verified_expert`: Verifies role is `EXPERT`, account status is `ACTIVE`, and verification status is `VERIFIED` (`HTTP 403 Forbidden` if pending, rejected, or suspended).
- `require_role(UserRole.ADMIN)`: Enforces administrative privileges (`HTTP 403 Forbidden` if non-admin).

---

## 8. AI-Assisted Analysis

### Inference Pipeline
```
Raw Image ──► Resize (256x256) ──► Center Crop (224x224) ──► Normalize (ImageNet Stats)
                                                                   │
                                                                   ▼
                                                       MobileNetV3 Feature Extractor
                                                                   │
                                                                   ▼
                                                          Linear Classifier Head
                                                                   │
                                                                   ▼
                                                            Softmax Function
                                                                   │
                                                                   ▼
                                                     Predicted Class & Confidence
```

### Decision-Support Terminology
- AI outputs are explicitly designated as **"Possible Conditions"** rather than certified diagnoses.
- System advisory notes emphasize that inferences are probabilistic suggestions intended for decision support.

### Dual-Mode Execution Strategy
1. **Real Model Mode (`ML_MODE=REAL`):**
   - Loads trained PyTorch model weights from `ml/artifacts/tomato_v1.pt`.
   - Executes convolutional feature extraction with MobileNetV3 Small.
   - Outputs multi-class probabilities, inference execution time (ms), and class rankings.
2. **Demo Mode Fallback (`ML_MODE=DEMO`):**
   - Automatically activates if model weights are absent or during isolated frontend testing.
   - Generates deterministic, symptom-aligned predictions tagged with `"is_demo_mode": true`.
   - Renders a visible **"DEMO MODE"** badge across all affected UI views.

---

## 9. Dataset

### Dataset Directory Structure
The dataset pipeline organizes agricultural image assets into standardized, reproducible partitions:

```
dataset/
├── raw/                # Original downloaded source imagery
├── processed/          # Cleaned, audited, and standard-dimension images
├── train/              # Training split (70%)
├── validation/         # Validation split (15%)
├── test/               # Hold-out evaluation test split (15%)
├── metadata/           # Structured CSV manifest linking imagery with field context
└── reports/            # Automated dataset audit logs, charts, and quality reports
```

### Metadata Fields
The dataset manifest (`dataset/metadata/dataset_metadata.csv`) tracks 12 standard attributes per sample:
- `image_id`: Unique identifier (e.g., `HS000001`).
- `image_path`: Normalized relative filesystem path.
- `crop`: Crop common name (e.g., `Tomato`).
- `disease`: Specific condition or disease class (e.g., `Early_Blight`, `Healthy`).
- `symptom`: Standardized visual symptom description.
- `location_region`: Geographic provenance region (e.g., `Karnataka`, `Tamil_Nadu`).
- `crop_stage`: Phenological growth stage (e.g., `Vegetative`, `Fruiting`).
- `image_source_type`: Data curation source classification.
- `quality_score`: Computational image quality metric ($0.0 - 1.0$).
- `expert_label`: Ground-truth label verified by an agricultural specialist.
- `split`: Dataset partition assignment (`train`, `validation`, `test`).
- `created_at`: Ingestion timestamp.

### Verified Dataset Statistics
Dataset statistics generated by the automated audit pipeline (`reports/dataset_report.json`):

| Metric | Verified Value |
| :--- | :--- |
| **Total Images** | **6,271** |
| **Train Set Partition** | 4,386 images (70.0%) |
| **Validation Set Partition** | 938 images (15.0%) |
| **Test Set Partition** | 947 images (15.0%) |
| **Target Crop** | Tomato (*Solanum lycopersicum*) |
| **Healthy Class Count** | 1,591 samples (25.4%) |
| **Early Blight Count** | 1,000 samples (15.9%) |
| **Late Blight Count** | 1,909 samples (30.4%) |
| **Septoria Leaf Spot Count** | 1,771 samples (28.2%) |
| **Standard Image Dimensions** | $256 \\times 256$ pixels (3-channel RGB) |
| **Privacy Compliance** | **100% Non-identifiable crop imagery.** Zero faces, farmer names, or private data. |

---

## 10. Expert Escalation

When automated analysis is inconclusive or represents high risk, HortiSentry initiates human expert escalation based on configurable thresholds defined in `config/escalation.yaml`:

```
                    ┌────────────────────────┐
                    │ Observation Submitted  │
                    └───────────┬────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
[ Quality Audit ]       [ Confidence Level ]    [ Disease Virulence ]
  Laplacian < 50.0        High: >= 0.85           High: Late Blight, Bacterial Spot
  Brightness < 30/> 225   Med:  0.60 - 0.84       Med:  Early Blight, Leaf Spot
                          Low:  < 0.60            Low:  Healthy, Powdery Mildew
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
                       [ Escalation Engine ]
                                │
            ┌───────────────────┴───────────────────┐
            ▼                                       ▼
     [ Auto-Escalate ]                       [ Standard Queue ]
  - Low confidence (< 0.60)               - High confidence (>= 0.85)
  - High-risk pathogen identified         - Normal/low risk level
  - Blurry or poor exposure image         - Image quality verified
  - Manual farmer request
```

### Configurable Escalation Policies
- **High Confidence ($\\ge 0.85$) + Low Risk:** Routed to normal monitoring; no automatic escalation.
- **Medium Confidence ($0.60 - 0.84$):** Advisory presented; expert review marked as *Recommended*.
- **Low Confidence ($< 0.60$):** Inconclusive inference; expert review marked as *Required*.
- **High-Risk Disease:** Severe pathogens (e.g., Late Blight, Bacterial Spot, Anthracnose, Fruit Rot) automatically trigger *Required* expert escalation regardless of confidence score.
- **Image Quality Anomaly:** Excessive blur or extreme exposure triggers escalation for re-inspection.
- **Manual Farmer Escalation:** Farmers can escalate any observation at their own discretion.

---

## 11. KPI & Analytics

### Primary KPI: Time to Expert Review
The primary efficiency metric evaluated by HortiSentry is the **Time to Expert Review**, defined as:

$$\\text{Time to Expert Review} = \\text{Expert Resolution Timestamp} - \\text{First Symptom Observation Timestamp}$$

### Lifecycle Timestamps Recorded
1. `first_symptom_time`: Farmer-reported timestamp when symptoms were first observed in the field.
2. `submitted_at`: Server timestamp when the observation was uploaded.
3. `ai_analysis_time`: Execution timestamp of the computer vision inference pipeline.
4. `escalation_time`: Timestamp when the case entered the expert review queue.
5. `started_at`: Timestamp when a verified expert opened the case for inspection.
6. `completed_at` / `review_timestamp`: Timestamp when the expert recorded the final diagnosis.
7. `resolution_time`: Timestamp when recommendations were delivered to the farmer.

### Operational KPI Benchmarks (Configured in `config/escalation.yaml`)
- **Baseline Traditional Response:** $\\mathbf{48.0\\text{ hours}}$ (manual escalation, telephone coordination, physical visits).
- **HortiSentry Target SLA:** $\\mathbf{\\le 6.0\\text{ hours}}$ turnaround time.
- **Model Inference Latency:** **$9.55\\text{ ms}$** average per-image inference on standard CPU ($104.7\\text{ images/second}$).

---

## 12. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER (React 18)                       │
│    Farmer Portal        │       Expert Portal      │     Admin Portal   │
│  (Observation Wizard)   │   (Case Review Queue)    │ (Telemetry & RBAC) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP / REST / JSON
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      API & SECURITY LAYER (FastAPI)                     │
│   FastAPI Router ──► Bearer JWT Auth ──► PBKDF2 Password Hashing        │
│   Rate Limiting  ──► CORS Middleware ──► File Upload Validator          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORE SERVICE LAYER                              │
│   ObservationService  ──► EscalationService ──► NotificationService     │
│   CropConfigLoader    ──► AuditService      ──► QualityAuditService     │
└──────────────────┬─────────────────────────────────┬────────────────────┘
                   │                                 │
                   ▼                                 ▼
┌──────────────────────────────────┐  ┌───────────────────────────────────┐
│       AI INFERENCE ENGINE        │  │       PERSISTENCE LAYER           │
│  PyTorch MobileNetV3-Small       │  │  SQLAlchemy 2.0 ORM Engine        │
│  Quality Preprocessor (OpenCV)   │  │  SQLite / PostgreSQL (Supabase)   │
│  Inference Fallback Simulator    │  │  Static Storage (/uploads)        │
└──────────────────────────────────┘  └───────────────────────────────────┘
```

- **Frontend Client:** React 18 single-page application built with Vite and Tailwind CSS.
- **Backend Core:** FastAPI asynchronous application exposing RESTful API endpoints.
- **Authentication:** Stateless Bearer token architecture signed using HMAC-SHA256.
- **Service Layer:** Modular domain services isolating business logic for observations, escalations, audits, and notifications.
- **Inference Engine:** PyTorch runtime executing MobileNetV3 Small transfer learning models.
- **Persistence Layer:** Relational storage handled by SQLAlchemy ORM with support for SQLite and PostgreSQL.

---

## 13. Technology Stack

### Frontend
- **Framework:** React 18.2
- **Language:** TypeScript 5.2
- **Build Tooling:** Vite 5.0
- **Styling:** Tailwind CSS 3.3 (Strict Light Theme: `#2E7D32`, `#1B5E20`, `#E8F5E9`, `#F8FAF8`)
- **Icons:** Lucide React
- **Unit & Integration Testing:** Vitest 0.34, Puppeteer-Core 25.10 (Headless Chrome DOM testing)

### Backend
- **Framework:** FastAPI 0.104
- **Server:** Uvicorn (ASGI) 0.23
- **Language:** Python 3.10+
- **Data Validation & Settings:** Pydantic v2, Pydantic-Settings
- **Configuration:** PyYAML 6.0

### Database & ORM
- **ORM:** SQLAlchemy 2.0
- **Default Database:** SQLite 3 (local zero-config database `hortisentry.db`)
- **Cloud Database Support:** PostgreSQL / Supabase via `psycopg2-binary` 2.9

### AI / Machine Learning & Computer Vision
- **Deep Learning Framework:** PyTorch 2.0+, Torchvision
- **Neural Architecture:** MobileNetV3 Small (pre-trained, fine-tuned classification head)
- **Computer Vision & Processing:** OpenCV (`opencv-python-headless` 4.8), Pillow (PIL) 10.0, NumPy 1.26

### Security & Authentication
- **Password Hashing:** PBKDF2-HMAC-SHA256 (100,000 rounds, 16-byte random salt)
- **Token Format:** RFC 7519 compliant HMAC-SHA256 JWT tokens
- **Authorization:** Role-Based Access Control (RBAC) dependency injection guards

### Containerization & Deployment
- **Container Engine:** Docker
- **Orchestration:** Docker Compose (v3.8)
- **Base Images:** `python:3.10-slim` (Backend), `node:18-alpine` $\rightarrow$ `nginx:alpine` (Frontend multi-stage)

---

## 14. Project Structure

```
HortiSentry/
├── backend/
│   ├── app/
│   │   ├── api/                 # REST API endpoints (auth, observations, expert, admin, crops, health)
│   │   ├── core/                # App configuration, security primitives, and constants
│   │   ├── database/            # Database engine connection and schema initializers
│   │   ├── evidence/            # Agricultural evidence source registry and retrieval
│   │   ├── ml/                  # Real PyTorch predictor & demo inference simulator
│   │   ├── models/              # SQLAlchemy database entities
│   │   ├── schemas/             # Pydantic request and response schemas
│   │   ├── services/            # Domain logic (ObservationService, ExpertService, EscalationService)
│   │   └── main.py              # FastAPI application factory and router registration
│   ├── tests/                   # Pytest test cases covering auth, observations, expert, and ML
│   ├── Dockerfile               # Production container definition for backend
│   └── requirements.txt         # Pinned backend Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components (CaseImageViewer, Badge, Modal, Navbar)
│   │   ├── layouts/             # AppLayout shell with navigation header and alerts
│   │   ├── pages/
│   │   │   ├── admin/           # AdminDashboard, UserManagement, CropManagement, AdminAnalytics
│   │   │   ├── expert/          # ExpertHome, ReviewQueue, CaseDetail, ExpertProfile, Status
│   │   │   ├── farmer/          # FarmerHome, ObservationWizard, History, Detail, AIReview
│   │   │   └── public/          # LandingPage, AboutPage, HowItWorks, LoginPage, RegisterPage
│   │   ├── services/            # Client-side API client functions (fetchHealth, createObservation)
│   │   ├── types/               # TypeScript interface definitions
│   │   ├── App.tsx              # Root router and state management
│   │   └── main.tsx             # Vite application entry point
│   ├── Dockerfile               # Multi-stage production Nginx container for frontend
│   ├── package.json             # NPM package manifests and scripts
│   ├── tailwind.config.js       # Tailwind CSS theme and color tokens
│   └── vite.config.ts           # Vite build and reverse proxy configuration
├── ml/
│   ├── artifacts/               # Serialized model weights (tomato_v1.pt, potato_v1.pt)
│   ├── checkpoints/             # Best checkpoint weights during training
│   ├── dataset.py               # PyTorch Dataset loader with augmentation transforms
│   ├── evaluate.py              # Test set evaluation and confusion matrix generator
│   ├── inference.py             # CLI inference utility for standalone image inspection
│   ├── model.py                 # MobileNetV3 Small PyTorch architecture definition
│   └── train.py                 # Training script with class weighting and validation tracking
├── dataset/
│   ├── metadata/                # Structured dataset manifests (dataset_metadata.csv)
│   ├── reports/                 # Dataset distribution and quality audit reports
│   └── raw/                     # Raw image repository
├── config/
│   ├── crops.yaml               # 32-crop dynamic catalog with Tamil and English naming
│   ├── escalation.yaml          # Confidence thresholds, risk classifications, and SLA targets
│   ├── ml.yaml                  # Model training hyperparameters
│   └── quality.yaml             # Image audit rules (blur variance, exposure boundaries)
├── reports/
│   ├── dataset_report.json      # Ingested dataset summary and quality metrics
│   ├── ml/                      # Test metrics, confusion matrix, and training curves
│   └── class_distribution.png   # Class distribution visualization chart
├── uploads/                     # Server media storage for uploaded crop photos
├── .env.example                 # Template for application environment variables
├── docker-compose.yml           # Local multi-container development orchestration
└── README.md                    # Project documentation
```

---

## 15. Database Overview

The relational schema comprises 12 entities managed by SQLAlchemy ORM:

```
┌──────────────┐         ┌─────────────────────────┐         ┌────────────────────┐
│    users     │1       *│       observations      │1       *│ observation_images │
│──────────────│─────────│─────────────────────────│─────────│────────────────────│
│ id (PK)      │         │ id (PK)                 │         │ id (PK)            │
│ role         │         │ user_id (FK)            │         │ observation_id(FK) │
│ email        │         │ crop_id (FK)            │         │ file_name          │
│ password_hash│         │ crop_stage              │         │ image_path         │
│ farmer_code  │         │ symptoms (JSON)         │         │ is_blur_detected   │
│ verif_status │         │ first_symptom_time      │         │ blur_score         │
│ acct_status  │         │ submitted_at            │         └────────────────────┘
└──────┬───────┘         │ risk_level              │
       │                 │ status                  │
       │                 └────────────┬────────────┘
       │                              │
       │                 ┌────────────┴────────────┬────────────────────────┐
       │1                │1                        │1                       │1
       │                 ▼*                        ▼*                       ▼*
       │          ┌──────────────┐          ┌──────────────┐         ┌──────────────┐
       │          │ predictions  │          │ escalations  │         │expert_reviews│
       │          │──────────────│          │──────────────│         │──────────────│
       │          │ id (PK)      │          │ id (PK)      │         │ id (PK)      │
       │          │ obs_id (FK)  │          │ obs_id (FK)  │         │ obs_id (FK)  │
       │          │ pred_class   │          │ reason       │         │ expert_id(FK)│◄─────┘
       │          │ confidence   │          │ status       │         │ final_cond   │
       │          │ risk_level   │          └──────────────┘         │ severity     │
       │          └──────────────┘                                   │ review_status│
       │                                                             └──────────────┘
       ▼*
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  audit_logs  │  │notifications │  │    crops     │  │  ai_reviews  │  │review_evid.  │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

### Entity Roles & Key Relationships
1. `users`: Stores farmer, expert, and admin accounts, passwords, roles, and verification statuses.
2. `crops`: Supported crop catalogue (`key`, `display_name`, active state).
3. `observations`: Primary case entity linking farmer, crop, symptoms, stage, location, and timestamps.
4. `observation_images`: Uploaded leaf files, dimensions, mime type, and blur/exposure scores.
5. `model_versions`: Registry of trained ML models (`version_name`, `model_architecture`).
6. `predictions`: AI inference output (`predicted_class`, `confidence`, `risk_level`, top-3 probabilities).
7. `escalations`: Escalation tracking records (`reason`, `status`, escalation timestamp).
8. `expert_reviews`: Authoritative specialist reviews (`final_condition`, `severity`, recommendations, status).
9. `ai_reviews`: Aggregated AI evidence synthesis records.
10. `review_evidence`: Citations from verified agricultural repositories.
11. `notifications`: In-app farmer and expert alerts.
12. `audit_logs`: Immutable security audit log.

---

## 16. API Overview

All API routes are served under the `/api` prefix:

### Authentication
- `POST /api/auth/register` — Register a new account (returns message; does not log in).
- `POST /api/auth/login` — Authenticate with email/password (returns JWT access token).
- `POST /api/auth/demo-login` — 1-Click quick evaluation login for pre-seeded personas.
- `GET /api/auth/me` — Retrieve the authenticated profile.

### Crop Configuration
- `GET /api/crops` — List supported horticultural crops with category/language filters.
- `GET /api/crops/{crop_id}` — Retrieve detailed configuration for a specific crop.

### Farmer Observations
- `POST /api/observations` — Submit a multipart form containing crop, symptoms, location, and leaf photo.
- `GET /api/observations` — List personal or cooperative observations.
- `GET /api/observations/{observation_id}` — Retrieve observation dossier with images, AI output, and expert status.
- `POST /api/observations/{observation_id}/analyze` — Re-trigger AI analysis on an existing observation.
- `POST /api/observations/{observation_id}/escalate` — Manually escalate an observation to the expert queue.

### Expert Portal (Requires `EXPERT` Role & `VERIFIED` Status)
- `GET /api/expert/dashboard/stats` — Retrieve expert review queue metrics and turnaround stats.
- `GET /api/expert/reviews` (or `/cases`) — List escalated cases with status, risk, and crop filters.
- `GET /api/expert/reviews/{review_id}` — Retrieve detailed case for side-by-side photo inspection.
- `POST /api/expert/reviews/{review_id}/complete` — Record authoritative expert diagnosis and farmer guidance.
- `POST /api/expert/reviews/{review_id}/request-info` — Request additional photos or details from the farmer.
- `GET /api/expert/reviewed` — List historically completed reviews.

### Administration & Governance (Requires `ADMIN` Role)
- `GET /api/admin/dashboard` — Platform telemetry, total counts, and queue depths.
- `GET /api/admin/analytics` — Time-to-Expert Review SLA benchmarks and distribution trends.
- `GET /api/admin/users` — Search and filter user accounts.
- `GET /api/admin/expert-verifications` — List expert verification applications.
- `POST /api/admin/expert-verifications/{user_id}/verify` — Approve, reject, or suspend an expert account.
- `PATCH /api/admin/users/{user_id}/toggle-status` — Toggle user account active status.
- `GET /api/admin/model-metrics` — Retrieve ML evaluation test metrics and confusion matrix.
- `GET /api/admin/dataset-metrics` — Retrieve dataset distribution and image audit metrics.
- `GET /api/admin/audit-logs` — Query immutable system audit logs.
- `GET /api/admin/crops` — List and manage crop catalogue.

### Notifications & System Health
- `GET /api/notifications` — Retrieve current user notifications.
- `PATCH /api/notifications/{notification_id}/read` — Mark notification as read.
- `POST /api/notifications/read-all` — Mark all user notifications as read.
- `GET /api/health` — System health check, database connectivity, and ML status.
- `GET /api/model-status` — Operational status of active vision models.
- `POST /api/predict` — Standalone image inference endpoint for ML testing.

---

## 17. Installation & Setup

### Prerequisites
- **Python:** Version 3.10 or higher
- **Node.js:** Version 18.0 or higher (with npm)
- **Git:** Version 2.30 or higher

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/HortiSentry.git
cd HortiSentry
```

### Step 2: Backend Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Initialize Database & Seed Catalogue
python -m app.database.init_db

cd ..
```

### Step 3: Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

cd ..
```

---

## 18. Environment Variables

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

### Configuration Variables Reference
```ini
# Application Mode
APP_ENV=development
SECRET_KEY=replace-with-a-secure-random-secret-key

# Database Connection (SQLite local default; supports PostgreSQL/Supabase)
DATABASE_URL=sqlite:///./hortisentry.db

# Machine Learning Engine
ML_MODE=REAL
CONFIDENCE_THRESHOLD=0.70
MODEL_PATH=ml/artifacts/tomato_v1.pt

# Upload Constraints
MAX_UPLOAD_SIZE_MB=10
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,webp
CROP_CONFIG_PATH=config/crops.yaml

# CORS Allowed Origins (Comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

> **SECURITY NOTE:** Never commit `.env` files containing real production secrets to source control.

---

## 19. Running the Application

### Option A: Local Development Server

#### 1. Start Backend Server
```bash
cd backend
# Windows:
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
# Linux/macOS:
python -m uvicorn app.main:app --reload --port 8000
```
- **Backend API:** `http://localhost:8000`
- **Interactive OpenAPI Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/api/health`

#### 2. Start Frontend Server
In a separate terminal:
```bash
cd frontend
npm run dev
```
- **Frontend App:** `http://localhost:5173`

---

### Option B: Docker Compose
To build and launch the complete multi-container stack:
```bash
docker-compose up --build
```
- Backend container maps to port `8000`.
- Frontend Nginx container maps to port `5173`.

---

## 20. Demo Workflow

Follow this end-to-end user scenario to test the complete platform:

1. **Farmer Registration:**
   - Navigate to `http://localhost:5173/register`.
   - Select **Farmer**, enter name, email, and password. Submit the form.
2. **Mandatory Sign-In:**
   - Notice the success banner: *"Registration successful! Please sign in with your new account."*
   - Enter credentials on the Login page and click **Sign In**.
3. **Submit Crop Observation:**
   - On the Farmer Dashboard, click **New Observation**.
   - Step 1: Select **Tomato** (*Solanum lycopersicum*).
   - Step 2: Upload a crop leaf photo (or use the sample button).
   - Step 3: Select the growth stage (e.g., *Vegetative*) and symptoms (e.g., *Dark lesions*, *Yellow spots*).
   - Step 4: Enter location details (Village, District, State) and submit.
4. **AI Screening Results:**
   - Observe immediate screening output showing the possible condition (e.g., *Possible Tomato Early Blight*), confidence percentage, and assigned risk tier.
5. **Automatic Escalation:**
   - If confidence is $< 85\%$ or the pathogen is high-risk, the system flags the case for expert review.
6. **Expert Application:**
   - Register a new account with the **Expert** role.
   - Upon sign-in, note that access is gated with a pending verification notice.
7. **Administrator Verification:**
   - Sign in as Admin (`admin@hortisentry.demo` / `admin123`).
   - Navigate to `/admin/expert-verifications`.
   - Locate the pending expert and click **Verify Expert**.
8. **Expert Review Execution:**
   - Sign in with the verified Expert account (`expert@hortisentry.demo` / `expert123`).
   - Open `/expert/queue` and click on the escalated case.
   - Inspect the leaf photo using the zoom controls and check image quality diagnostics.
   - Select the validated diagnosis, assign severity, write farmer guidance, and submit.
9. **Farmer Receives Resolution:**
   - Log back in as the Farmer. Open `/farmer/observations`.
   - Open the submitted case and observe the updated status (**Expert Reviewed**) with the specialist's assessment.
10. **Admin Telemetry Review:**
    - Log in as Admin and open `/admin/analytics` to verify that the **Time to Expert Review** metric has updated.

---

## 21. Testing

The platform includes automated testing across unit, integration, and browser DOM layers:

### Test Suites Implemented
- **Authentication Tests:** Registration-login separation, PBKDF2 password hashing, JWT token lifecycle.
- **Authorization Tests:** Role-based access control, pending expert rejection (`HTTP 403`), admin route protection.
- **Farmer Workflow Tests:** Multi-step wizard input validation, observation creation, personal history queries.
- **Expert Verification Tests:** Admin verification transitions (`PENDING` $\rightarrow$ `VERIFIED`, `REJECTED`, `SUSPENDED`).
- **Image Validation Tests:** Unsupported extension rejection, corrupt payload detection, Laplacian blur scoring.
- **AI Inference Tests:** MobileNetV3 tensor transformation, dual-mode fallback, probability distribution validation.
- **Headless Chrome DOM Tests:** Full DOM integration verification simulating multi-role user sessions using Puppeteer.

### Running Backend Tests
```bash
cd backend
.\venv\Scripts\python.exe -m pytest backend/tests -v
```

### Running Frontend Tests
```bash
cd frontend
npm test
```

### Running Headless Chrome DOM Verification
```bash
node scratch/dom_verification.cjs
```

### Verified Test Results
- **Backend Pytest Suite:** **53 / 53 passed (100%)**
- **Frontend Vitest Suite:** **6 / 6 passed (100%)**
- **Headless Chrome DOM Verification:** **23 / 23 end-to-end checks passed (100%)**

---

## 22. Security & Privacy

- **Password Hashing:** Passwords are never stored in plaintext. They are hashed using PBKDF2-HMAC-SHA256 with 100,000 iterations and a unique 16-byte cryptographic salt per user.
- **Stateless Tokens:** Authentication sessions use RFC 7519 compliant HMAC-SHA256 JWT tokens with a 7-day expiration.
- **Strict Role-Based Access Control:** Backend dependency guards enforce role permissions on every sensitive endpoint.
- **Expert Gating:** Selecting the "Expert" role does not grant portal privileges until an Administrator verifies credentials.
- **Secure File Upload Pipeline:** Uploaded images are validated against allowed MIME types and magic bytes, stripped of execution privileges, and restricted to a 10MB limit.
- **Non-Identifiable Farmer Privacy:** Farmers are assigned pseudonymous codes (`HS-FARMER-XXXX`). Field locations are stored at coarse regional granularity (Village, District, State).
- **Zero Facial or Personal Imagery:** The dataset and image processing pipelines process crop foliage exclusively; personal imagery is strictly rejected.
- **Audit Trails:** Security-sensitive events (logins, registrations, status changes, expert reviews) are recorded in an append-only `audit_logs` table.

---

## 23. Ethical Considerations

- **Decision Support, Not Replacement:** AI outputs are advisory tools designed to accelerate specialist triage. They do not replace certified agricultural extension officers.
- **Confidence vs. Certainty:** A high confidence score indicates model certainty relative to its training distribution, not an absolute guarantee of biological reality.
- **Mitigating Dataset Bias:** Training datasets predominantly feature specific cultivars under controlled lighting. Field predictions must account for regional variations.
- **Farmer Protection:** System policies explicitly prohibit penalizing farmers or conditioning agricultural subsidies on automated AI outputs.
- **Human Oversight:** High-consequence decisions involving quarantine pathogens or major chemical interventions require human expert review.

> *"AI-generated results are intended for decision support and should not replace professional agricultural assessment."*

---

## 24. Risk Management

| Risk Factor | Severity | Impact | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Incorrect AI Prediction** | High | Misdiagnosis leading to incorrect crop management | Automated escalation of low-confidence predictions to verified human specialists; clear decision-support disclaimers |
| **Poor Image Quality (Blur/Exposure)** | Medium | Compromised feature extraction and inaccurate classification | Automated Laplacian blur variance and pixel exposure screening; immediate re-take guidance for farmers |
| **Dataset & Regional Bias** | High | Reduced model sensitivity on local or atypical cultivars | Stratified data collection across multiple agricultural zones (Karnataka, Maharashtra, Tamil Nadu); ongoing data expansion |
| **Unauthorized Expert Access** | High | Incompetent or malicious advice provided to farmers | Mandatory administrator verification workflow before expert privileges are granted; full audit logging |
| **Data Leakage & Privacy Breach** | High | Exposure of farmer locations or operational data | Pseudonymous farmer codes; coarse geographic resolution; stateless JWT authentication; strictly non-identifiable foliage imagery |
| **AI Service Downtime** | Medium | Interruption of immediate screening feedback | Graceful fallback to heuristic demo screening with visible UI indicator; asynchronous expert queueing |
| **Model Concept Drift** | Medium | Accuracy degradation as seasonal pathogens mutate | Model versioning in database (`model_versions`); continuous evaluation metrics tracking against hold-out test sets |

---

## 25. Limitations

- **Dataset Scope:** The dedicated PyTorch model currently focuses on Tomato disease classes (with Potato support). Other crops in the 32-crop catalog use heuristic knowledge rules.
- **Visual Symptom Ambiguity:** Different pathogens (e.g., early-stage fungal leaf spots vs. physiological nutrient deficiencies) can present near-identical visual phenotypes.
- **Lighting & Sensor Variability:** Smartphone camera quality, direct glare, shadow occlusions, and severe angle tilts can affect model confidence.
- **Human Review Turnaround Dependency:** Time to expert review depends on the availability and responsiveness of verified human specialists.
- **Prototype Scope:** While functional and integration-tested, field deployment at scale requires regional extension agency partnerships and agronomic validation.

---

## 26. Future Improvements

- **Broader Vision Model Coverage:** Train dedicated deep neural networks for additional high-value horticultural crops (e.g., Chilli, Banana, Mango).
- **Explainable AI (XAI):** Integrate Grad-CAM heatmaps to visualize the exact leaf regions driving model predictions.
- **Progressive Web App (PWA) & Offline Mode:** Implement local service workers and IndexedDB to cache observations submitted in low-connectivity rural zones.
- **Expanded Multilingual Support:** Expand interface localization beyond English and Tamil to Hindi, Kannada, Telugu, and Marathi.
- **Automated Weather Context Integration:** Incorporate regional temperature, humidity, and rainfall feeds into risk assessment heuristics.
- **Continuous Learning Loop:** Mechanism for confirmed expert diagnoses to feed back into re-training datasets after anonymization and quality validation.

---

## 27. Deployment

### Containerized Deployment (Docker Compose)
The repository includes production Dockerfiles for both services and a top-level `docker-compose.yml`:

```bash
# Build and run containers in detached mode
docker-compose up -d --build
```
- **Backend Container:** Runs Python 3.10 slim, installs dependencies, initializes database migrations, and serves Uvicorn on port `8000`.
- **Frontend Container:** Multi-stage build compiling TypeScript/Vite into static assets and serving via Nginx on port `5173`.

### Cloud Database Integration
To connect HortiSentry to a managed cloud database (e.g., Supabase, AWS RDS, PostgreSQL):
1. Update `DATABASE_URL` in `.env`:
   ```ini
   DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```
2. Initialize tables on the new database:
   ```bash
   python -m app.database.init_db
   ```

*(Note: Production cloud orchestration using Kubernetes or cloud VM instances is prepared via the Docker configuration.)*

---

## 28. Disclaimer

HortiSentry is an AI-assisted software platform for crop symptom observation and decision support. AI predictions are not guaranteed diagnoses. Agricultural experts should be consulted for uncertain, high-risk or critical cases.

---

## 29. License

License information will be added by the project maintainers.
