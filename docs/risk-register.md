# HortiSentry — Risk Register

| Risk ID | Risk Description | Likelihood | Impact | Mitigation Strategy | Owner | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R-01** | Poor image quality (blur / low lighting) causing inaccurate AI prediction. | High | High | Integrated client & server-side blur validator; auto-flag low quality images for expert review. | ML Engineer | Active |
| **R-02** | User misinterpreting AI assistance output as certified/guaranteed diagnosis. | Medium | Critical | Explicit UI disclaimers ("AI-Assisted Observation"); prohibition of auto-generating chemical treatment dosages. | UX Lead | Active |
| **R-03** | Model overfitting to benchmark dataset lighting/background conditions. | Medium | High | Data augmentation (color jitter, rotation, cropping); mandatory expert override capability. | ML Engineer | Active |
| **R-04** | Farmer connectivity loss in rural areas during observation submission. | High | Medium | Responsive form caching; graceful offline error boundary with retry prompts. | Frontend Dev | Active |
| **R-05** | Unauthorized access to raw images or location data. | Low | High | Data minimization (coarse regional locations only); strict upload filename sanitization & UUIDs. | Security Lead | Active |
| **R-06** | Concept drift due to seasonal crop disease evolution. | Medium | Medium | Active model versioning (`model_versions` table); logging expert corrections for retraining. | Lead Architect | Active |
