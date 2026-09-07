# HortiSentry — Expert Review Workflow Specification

**Phase:** Phase 5 Expert / Cooperative Dashboard  

---

## 1. Overview & Data Governance Principles

The Expert Review Workflow provides human-in-the-loop validation for agricultural disease observations. Key principles:

1. **Dual Prediction Preservation:** The database never overwrites the original AI prediction when an expert overrides a diagnosis. Both `predictions.predicted_class` and `expert_reviews.expert_prediction` are stored independently for downstream model evaluation.
2. **Deterministic Triage Routing:** Observations are automatically escalated when `confidence < 0.70` or `is_blur_detected = true` / `is_exposure_issue = true`, or when manually requested by farmers (`reason = MANUAL_FARMER_REQUEST`).
3. **Turnaround Tracking:** Operational turnaround metric:
   $$\text{Turnaround Duration} = t_{\text{expert\_completed\_at}} - t_{\text{symptom\_observed\_at}}$$

---

## 2. Review Lifecycle & Status Transitions

```
[Observation Submitted]
          ↓
[Auto Quality / Confidence Evaluation]
     ├── High Confidence & Good Quality ──> [Status: SUBMITTED / COMPLETED]
     └── Low Confidence / Blur / Manual  ──> [Status: PENDING_REVIEW]
                                                    ↓ (Expert Opens Case)
                                           [Status: UNDER_REVIEW]
                                                    ↓
                                ┌───────────────────┴───────────────────┐
                                ↓                                       ↓
                   [Expert Decision: Complete]             [Expert Decision: Request Info]
                                ↓                                       ↓
                     [Status: COMPLETED]                     [Status: NEEDS_INFO]
                     (Escalation: RESOLVED)
```

---

## 3. Ground-Truth Data Capture Schema

Each completed review records:
- `review_id` (UUID)
- `observation_id` (UUID)
- `reviewer_id` (UUID)
- `expert_prediction` (String)
- `expert_notes` (Text)
- `started_at` (UTC Timestamp)
- `completed_at` (UTC Timestamp)
- `status` (`COMPLETED`)

This structured dataset provides verified ground-truth labels for Phase 7 PyTorch transfer learning model retraining.
