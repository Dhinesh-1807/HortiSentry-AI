# HortiSentry — Stakeholder Trade-off Analysis

## Executive Summary
Designing an agricultural decision support tool creates inherent design friction between the priorities of two primary user groups: **Farmers** and **Agricultural Experts / Cooperative Reviewers**.

---

## Conflict Analysis

```mermaid
quadrantChart
    title Farmer Usability vs. Expert Diagnostic Depth
    x-axis Low Information Depth --> High Information Depth
    y-axis Complex / Slow UI --> Simple / Fast UI
    quadrant-1 Optimal HortiSentry Balanced Zone
    quadrant-2 Over-simplified (High speed, poor diagnostic value)
    quadrant-3 Sub-optimal (Slow, poor diagnostic value)
    quadrant-4 Over-burdensome (Rich data, low farmer adoption)
    "Unstructured Chat/SMS": [0.2, 0.8]
    "Paper Logbook": [0.3, 0.2]
    "Exhaustive 20-Page Form": [0.9, 0.1]
    "HortiSentry Observation Wizard": [0.75, 0.85]
```

### Stakeholder Group 1: The Farmer
- **Priorities:** Fast reporting, minimal typing, simple visual touch chips, immediate feedback, non-intrusive location tracking.
- **Pain Points:** Overwhelmed by lengthy forms or technical jargon; poor network connectivity in remote fields.

### Stakeholder Group 2: The Agricultural Expert / Cooperative Reviewer
- **Priorities:** High-resolution clear crop images, precise growth stage, detailed symptom checklist, approximate location context, model confidence breakdown.
- **Pain Points:** Receiving blurry, context-free photos via unstructured messaging apps (e.g. WhatsApp) without growth stage or location data.

---

## Architectural Resolution & Compromise

HortiSentry resolves this conflict through a **Structured Multi-Step Guided Submission Wizard**:
1. **Mandatory Core Fields (Low Friction):** Crop selection (1 tap), Photo upload (1 tap), Growth stage (1 tap), Selectable symptom chips (1-2 taps), Village/District selection dropdown.
2. **Optional Extended Information:** Free-text notes and exact symptom onset date picker.
3. **Structured Expert Panel:** Presents the expert with a unified dashboard combining high-res image pan/zoom, farmer symptom selections, and AI prediction breakdown on a single screen.
