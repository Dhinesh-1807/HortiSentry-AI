# HortiSentry — Final Project & Academic Evaluation Report

**Project Title:** HortiSentry — AI-Powered Horticultural Disease Observation and Expert Escalation System  
**Tagline:** See Early. Act Smart. Protect Crops.  
**Domain:** Artificial Intelligence + Computer Vision + Horticultural Crop Protection + Expert Decision Support  
**Target Crop:** Tomato (*Solanum lycopersicum*)  
**Evaluation Date:** September 2, 2026  

---

## 1. Abstract
HortiSentry is an AI-powered 3-tier horticultural observation and decision support system designed to assist farmers in early disease detection while providing seamless escalation to human agricultural experts. Operating on a lightweight MobileNetV3 Small PyTorch classifier (`tomato-v1`), HortiSentry achieves **99.37% test accuracy** and **0.9927 macro F1** across four canonical tomato disease classes. The system incorporates automated OpenCV image quality auditing, AI confidence-based escalation ($< 0.70$), and strict database decision preservation.

---

## 2. Problem Statement
Smallholder horticultural farmers face substantial crop loss due to misidentified fungal and bacterial foliage pathogens. Existing mobile plant diagnostic tools often provide opaque, uncalibrated AI predictions without expert verification or image quality controls, leading to improper chemical application and yield loss.

---

## 3. Motivation
Constructing an intelligent agricultural system requires bridging the gap between automated computer vision and authoritative human expert oversight. HortiSentry introduces a human-in-the-loop escalation pipeline that prioritizes farmer decision support over unverified diagnostic certification.

---

## 4. System Objectives
1. **Mobile-First Farmer Experience:** Simple observation submission with visual image quality pre-checks.
2. **Real-Time ML Inference:** Low-latency PyTorch classification ($< 30\text{ ms}$ inference speed).
3. **Automated Expert Escalation:** Automatic routing of low-confidence ($< 0.70$), poor-quality, or farmer-requested cases to cooperative agronomists.
4. **Authoritative Decision Preservation:** Independent storage of AI predictions and expert review overrides for auditability.
5. **Responsible AI Framework:** Explicit disclaimers, privacy protections, and non-chemical cultural guidance.

---

## 5. Existing System Limitations
Traditional farm diagnostic applications lack:
- Image quality pre-validation (blur/exposure checks prior to inference).
- Automatic expert escalation for low-confidence model predictions.
- Separation of ground-truth expert corrections from initial AI inference logs.

---

## 6. Proposed HortiSentry System
HortiSentry resolves these challenges by introducing a 3-tier architecture with integrated OpenCV quality checks, PyTorch MobileNetV3 inference, decision escalation state machines, and a dedicated Expert Review Dashboard.

---

## 7. System Architecture
- **Client Tier:** React 18 + Vite + TypeScript (Farmer UI & Expert Dashboard).
- **Backend Tier:** FastAPI async REST endpoints + Pydantic validation.
- **ML Tier:** PyTorch `MobileNetV3 Small` (`tomato-v1`) with fallback `DemoPredictor`.
- **Database Tier:** SQLite with SQLAlchemy ORM schemas.

---

## 8. User Workflows
1. **Farmer Workflow:** Home $\rightarrow$ New Observation $\rightarrow$ Crop Selection $\rightarrow$ Image Upload & Quality Check $\rightarrow$ Symptoms $\rightarrow$ Submit $\rightarrow$ Instant AI Result $\rightarrow$ Track Status.
2. **Expert Workflow:** Dashboard $\rightarrow$ Queued Cases $\rightarrow$ Image & Symptom Inspection $\rightarrow$ Validate/Override AI Prediction $\rightarrow$ Complete Review / Request Info.

---

## 9. Dataset Summary
- **Total Images:** 6,271 tomato leaf images across 4 classes.
- **Partitions:** 4,386 Train (70%) / 938 Validation (15%) / 947 Test (15%).
- **Quality Audit:** 6,168 Good / 102 Warning / 1 Reject (`Late_Blight_03659` severe blur, excluded from training).
- **Master Test MD5:** `d501546c433bc0e204821754144bc5d9`.

---

## 10. Image Quality Pipeline
Uses OpenCV Laplacian variance ($\text{threshold} = 100.0$) for blur detection and brightness histograms ($[40, 220]$) for exposure auditing before passing images to inference.

---

## 11. ML Methodology & Architecture
- **Backbone:** PyTorch `mobilenet_v3_small` pretrained on ImageNet.
- **Head:** Linear classifier ($1024 \rightarrow 4$).
- **Loss Function:** `CrossEntropyLoss` with inverse class-frequency weights ($[0.9861, 1.5664, 0.8213, 0.8850]$).

---

## 12. Model Training Log
- **Epochs:** 10 max (Best epoch: **Epoch 9**).
- **Best Validation Accuracy:** **99.68%** (Val Loss: `0.0111`).
- **Optimizer:** AdamW ($\text{LR} = 0.001$, Weight Decay $= 0.0001$).

---

## 13. Model Evaluation (Untouched 947 Test Images)
- **Overall Accuracy:** **99.37%** (941 / 947 correct)
- **Macro Precision:** **0.9923**
- **Macro Recall:** **0.9932**
- **Macro F1 Score:** **0.9927**
- **Weighted F1 Score:** **0.9937**

---

## 14. Expert Escalation Engine
Evaluates AI confidence and image quality. Sets case status to `PENDING_REVIEW` if confidence $< 0.70$, quality is rejected, or farmer manually requests expert assistance.

---

## 15. Security Safeguards
- Path traversal mitigation via UUID sanitization.
- File size limit enforcement ($10\text{MB}$).
- Allowed image extension white-listing and PIL header checks.

---

## 16. Testing & Verification
- **Backend Pytest:** `36 / 36 PASSED`
- **Frontend Vitest:** `6 / 6 PASSED`
- **Frontend Build:** Clean Vite build (`0 errors`)
- **E2E REST Script:** `13 / 13 APIs PASSED`, `4 / 4 Scenarios PASSED`

---

## 17. System Results & Measured Latency
- **System Health API:** `19.55 ms`
- **Model Status API:** `5.99 ms`
- **PyTorch CPU Inference:** `9.55 ms` / image (`30.73 ms` full REST pipeline)

---

## 18. System Limitations
1. **Domain Shift:** Studio benchmark dataset performance may vary under ambient solar radiation or leaf background clutter.
2. **Crop Scope:** Currently trained exclusively for Tomato (*Solanum lycopersicum*).

---

## 19. Responsible AI Principles
- Prominently displays: *"Decision Support, Not Diagnostic Certification"*.
- Excludes direct chemical dosage recommendations.
- Guarantees farmer location privacy.

---

## 20. Future Enhancements
1. Multi-crop expansion (Potato, Pepper, Cassava) via `config/crops.yaml`.
2. Edge mobile deployment using PyTorch Mobile / ONNX Runtime.

---

## 21. Conclusion
HortiSentry successfully demonstrates a robust, high-accuracy, 3-tier horticultural observation system combining state-of-the-art computer vision with ethical human-in-the-loop expert escalation.
