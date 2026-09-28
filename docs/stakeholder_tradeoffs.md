# HortiSentry Stakeholder Trade-off Analysis & Architecture Alignment

## Overview
Designing an AI-assisted agricultural disease observation system requires balancing the competing priorities of multiple key stakeholders: smallholder farmers, agricultural cooperatives/buyers, and agronomist experts. HortiSentry avoids treating any single stakeholder as automatically correct, instead implementing a balanced design strategy that aligns technical capabilities with practical field constraints.

---

## 1. Stakeholder Perspectives & Priorities

```
                      ┌──────────────────────────────┐
                      │    Smallholder Farmers       │
                      │ • Simple reporting           │
                      │ • Fast feedback              │
                      │ • Minimal friction           │
                      └──────────────┬───────────────┘
                                     │
                                     ▼
┌──────────────────────────────┐           ┌──────────────────────────────┐
│  Agricultural Cooperatives   │ ◄───────► │    Agronomist Experts        │
│ • Produce quality assurance  │           │ • Complete observation data  │
│ • Risk reduction             │           │ • Good quality photos        │
│ • Traceable case history     │           │ • Manageable queue volume    │
└──────────────────────────────┘           └──────────────────────────────┘
```

### 1.1 Smallholder Farmer Perspective
- **Core Priorities:**
  - Simple, mobile-friendly observation reporting.
  - Minimal data-entry effort (quick multi-choice symptom checkboxes).
  - Fast, immediate visual feedback and actionable management guidance.
  - Easy photo upload without rigid equipment demands.
  - Direct access to verified human agronomist assistance when needed.
- **Key Concerns:**
  - Excessive mandatory form fields or complex technical jargon decrease usability and adoption.
  - Frequent false alarms or unnecessary case rejections increase farmer frustration and reduce trust in digital tools.

### 1.2 Agricultural Cooperative / Buyer Perspective
- **Core Priorities:**
  - Maintaining produce quality across member farms.
  - Early identification of high-risk quarantine diseases (e.g. *Phytophthora infestans* / Late Blight).
  - Standardized, audit-ready disease observation records.
  - Risk reduction across regional supply chains.
  - Reliable expert verification before issuing major spray/quarantine advisories.
- **Key Concerns:**
  - Insufficient verification or overly lenient AI screening might allow severe disease outbreaks to spread undetected, impacting yield and crop valuation.

### 1.3 Agronomist Expert Perspective
- **Core Priorities:**
  - Receiving complete observation context (crop stage, location, symptoms, clear leaf photos).
  - Clear AI confidence scores and risk indicators to prioritize urgent cases.
  - A manageable review queue volume that permits thorough diagnostic assessment.
  - Clear distinction between AI decision support and certified human expert diagnosis.
- **Key Concerns:**
  - Over-escalation of routine, low-risk cases overloads the expert queue, leading to reviewer fatigue and delayed responses for critical cases.

---

## 2. Core System Trade-Offs & HortiSentry Design Balances

HortiSentry explicitly addresses four fundamental trade-offs:

### Trade-Off 1: Farmer Acceptance vs. Cooperative Quality Assurance
- **The Dilemma:** Maximizing farmer adoption requires ultra-fast submission with minimal required fields. However, cooperative quality assurance requires rigorous data collection.
- **HortiSentry Balance:** HortiSentry implements a **2-minute structured wizard**. Farmers select coarse location and check pre-filtered visual symptoms, while automated metadata (timestamps, crop registry lookup, image quality heuristics) populates background fields automatically.

### Trade-Off 2: Fast Reporting vs. Detailed Data Collection
- **The Dilemma:** Collecting comprehensive environmental and micro-climate data improves diagnostic precision, but creates submission friction for field workers.
- **HortiSentry Balance:** The system prioritizes essential visual evidence (leaf photo + key symptoms). Detailed environmental evidence is optionally enriched by HortiSentry's **AI Evidence Review Engine**, which retrieves grounded ICAR/TNAU agricultural evidence automatically based on the reported crop and symptoms.

### Trade-Off 3: High Sensitivity / Escalations vs. Expert Workload
- **The Dilemma:** Setting a very high escalation threshold routes almost every observation to human experts, overloading agronomists. Conversely, setting a low threshold risks missing subtle early-stage infections.
- **HortiSentry Balance:** HortiSentry employs an **engineering confidence threshold of 0.70** combined with multi-factor risk rules:
  - High confidence ($\ge 0.70$) + Low Risk $\rightarrow$ Routine monitoring guidance issued directly to farmer.
  - Low confidence ($< 0.70$) OR High-Risk Disease (Late Blight) OR Poor Image Quality $\rightarrow$ Automated escalation to Expert Review Queue.

### Trade-Off 4: Automated AI Screening vs. Need for Human Verification
- **The Dilemma:** Fully automated AI predictions are instant and low-cost, but carry risk of visual misdiagnosis. Pure human expert review is accurate, but slow and unscalable for thousands of daily observations.
- **HortiSentry Balance:** AI is positioned strictly as **AI-Assisted Agricultural Decision Support**. The AI screens 100% of incoming submissions instantly. High-confidence routine cases receive immediate guidance, while complex, borderline, or high-risk cases are escalated to certified agronomists with pre-computed AI evidence summaries.

---

## 3. Summary Alignment Matrix

| Dimension | Primary Goal | Mitigation / Balance Strategy |
| :--- | :--- | :--- |
| **Farmer Effort** | Minimal data entry | Visual symptom checkboxes + auto-detected image quality |
| **Cooperative Security** | Produce quality assurance | Automated escalation for high-risk pathogens (*Late Blight*) |
| **Expert Efficiency** | Manageable queue volume | AI filters out high-confidence healthy/routine observations |
| **Diagnostic Safety** | Avoid AI hallucination | AI outputs labeled "AI Evidence Review"; 0.70 confidence threshold enforces human escalation |
