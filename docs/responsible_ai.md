# HortiSentry Responsible AI & Decision Support Principles

## Core Responsible AI Guardrails

> [!IMPORTANT]
> **AI Role Definition:**
> HortiSentry Vision Models (`tomato-v1`, `potato-v1`) provide **AI-assisted agricultural decision support** and visual symptom observation. They **DO NOT** issue statutory diagnostic certifications or agricultural expert guarantees.

### 1. Phrasing & Nomenclature Safeguards
- All outputs use terms like `"AI-Assisted Visual Review"`, `"Symptom Candidate"`, and `"AI Decision Support"`.
- Never claim an AI output is an `"Expert Review"` unless verified by a certified human expert.

### 2. Confidence & Expert Escalation Policy
- **Threshold:** Set to **0.70** (`CONFIDENCE_THRESHOLD = 0.70`).
- Any prediction yielding top confidence $< 0.70$ is automatically flagged with `needs_expert_review: true`.
- Low-confidence observations are escalated to human agronomist verification.

### 3. Out-of-Domain & Domain Shift Guardrails
- **Controlled vs In-Situ Field Foliage:**
  - Models trained primarily on laboratory/controlled backgrounds may suffer degradation on complex field backgrounds.
  - HortiSentry audits in-situ field image performance separately (e.g. 16 field test set samples in `potato-v1.1-dataset`).
- **Unseen Diseases / Novel Pathogens:**
  - If visual symptoms do not strongly match the 3 trained potato classes or 4 tomato classes, confidence drops below 0.70, triggering escalation to the evidence review engine or expert queue.

### 4. Human-in-the-Loop Integration
Human expert escalation is triggered for:
- Low AI model confidence ($< 0.70$)
- Poor or warning-level image quality
- Conflicting evidence between vision predictions and agricultural knowledge base
- Severe / high-risk plant disease alerts
- Farmer-requested verification
