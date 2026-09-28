# HortiSentry — System Risk Register

| Risk ID | Risk Description | Likelihood | Impact | Mitigation Strategy | Owner | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R-01** | Poor image quality (blur / low lighting) causing inaccurate AI prediction. | High | High | Integrated server-side blur & exposure validator; auto-flag low quality images for expert review. | ML Engineer | Active |
| **R-02** | User misinterpreting AI assistance output as certified/guaranteed diagnosis. | Medium | Critical | Explicit UI disclaimers ("AI-Assisted Agricultural Review"); probabilistic language ("consistent with"); human expert escalation. | UX / AI Safety | Active |
| **R-03** | Model overfitting to laboratory/controlled background conditions. | Medium | High | Data augmentation (color jitter, rotation, cropping); separate in-situ field test set evaluation; mandatory expert override capability. | ML Engineer | Active |
| **R-04** | Farmer connectivity loss in rural areas during observation submission. | High | Medium | Responsive form caching; graceful offline error boundary with retry prompts. | Frontend Dev | Active |
| **R-05** | Unauthorized access to raw images or location data. | Low | High | Data minimization (coarse regional locations only); strict upload filename sanitization & UUIDs. | Security Lead | Active |
| **R-06** | Concept drift due to seasonal crop disease evolution. | Medium | Medium | Active model versioning (`tomato-v1`, `potato-v1`); logging expert corrections for future retraining. | Lead Architect | Active |
| **R-07** | Expert queue overload due to high escalation volume. | Medium | High | 0.70 confidence routing threshold filters out high-confidence routine cases; AI evidence engine pre-generates grounded summaries for experts. | Product Lead | Active |
| **R-08** | Misclassifying unsupported crops using trained tomato/potato models. | Low | High | Crop-Aware Prediction Service (`CropAwarePredictionService`); unsupported crops route directly to AI Evidence Review without fake vision scores. | System Architect | Active |
