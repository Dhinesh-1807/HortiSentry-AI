# HortiSentry — Ethical & Responsible AI Framework

## 1. Principles of Responsible AI Assistance
HortiSentry adheres strictly to ethical standards for AI deployment in agriculture:

1. **AI as Assistance, Not Authority:** HortiSentry is designed explicitly as a decision support prototype. The platform **never** presents AI outputs as authoritative certified diagnoses.
2. **Prohibition of Direct Chemical Dosage Advice:** AI models are prone to confidence miscalibrations. To prevent crop damage, environmental contamination, or farmer harm, HortiSentry **never** auto-generates chemical pesticide treatment advice based solely on ML outputs. Treatment advice remains under the strict purview of human agricultural experts.
3. **Transparent Uncertainty Communication:** When AI confidence falls below 0.70 or visual quality is inadequate, the UI clearly displays an **"Expert Review Recommended"** banner rather than presenting a false high-confidence classification.
4. **Human-in-the-Loop Oversight:** Farmers retain the unconditional right to escalate any case to human expert review. Experts can validate or override any AI recommendation.

---

## 2. Privacy & Data Protection
- **Data Minimization:** Only coarse location identifiers (Village, District, State) are requested. No exact street addresses, GPS tracking, national identity numbers, or personal documents are required.
- **Non-Identifiable Image Processing:** Images are stored using anonymized UUID filenames.
