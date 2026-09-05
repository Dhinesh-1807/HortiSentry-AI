# HortiSentry — Data Flow Specification

## Overview
This document describes the end-to-end data lifecycle within HortiSentry, detailing how information moves from farmer input through backend validation, ML inference, decision-engine escalation, and expert resolution.

---

## High-Level Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Farmer
    participant UI as React Frontend
    participant API as FastAPI Backend
    participant ML as ML Service
    participant DB as SQLite DB
    actor Expert

    Farmer->>UI: Select Crop (Tomato), Stage, Symptoms, Location
    Farmer->>UI: Upload Crop Image
    UI->>API: GET /api/crops (Fetch config)
    API-->>UI: Dynamic Crop Configuration
    Farmer->>UI: Submit Observation
    UI->>API: POST /api/observations (Multipart Upload)
    API->>API: Execute Image Quality Inspector (Blur/Exposure)
    API->>DB: Save Observation, User & Image Metadata
    API->>ML: Pass Image Tensor to Predictor
    ML-->>API: Return Prediction JSON (Class, Confidence, Demo Flag)
    API->>API: Evaluate Escalation Threshold (CONFIDENCE_THRESHOLD = 0.70)
    alt Confidence >= 0.70 & Quality OK
        API-->>UI: High-Confidence AI-Assisted Output
    else Confidence < 0.70 or Poor Quality
        API->>DB: Insert Escalation & Expert Review Queue Records
        API-->>UI: AI Output + "Expert Review Recommended" Banner
    end
    Expert->>API: GET /api/expert/reviews (Pending Queue)
    API-->>Expert: List Pending Case Queue
    Expert->>API: POST /api/expert/reviews/{id}/complete (Submit Diagnosis)
    API->>DB: Update Review Status to COMPLETED & Timestamp
```

---

## Timestamps & Temporal Performance Metrics

HortiSentry explicitly records timestamps at each operational milestone to measure turnaround efficiency:

1. `symptom_observed_at`: Time when farmer first observed symptoms in the field.
2. `submitted_at`: Time when observation payload was submitted to FastAPI.
3. `started_at`: Time when an expert opened and initiated review of an escalated case.
4. `completed_at`: Time when expert saved authoritative guidance and closed the case.

**Primary Operational Performance Metric:**
$$\text{Time to Useful Review} = t_{\text{completed\_at}} - t_{\text{symptom\_observed\_at}}$$
