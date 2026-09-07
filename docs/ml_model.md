# HortiSentry Multi-Crop Vision Model Architecture & Registry Guide

## Overview
HortiSentry employs a modular, extensible Multi-Crop Vision Architecture designed to handle active crop-specific PyTorch models alongside fallback AI visual symptom evaluation.

```
                  Client Upload (POST /api/predict)
                                 │
                                 ▼
                        ImageQualityService
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
               Quality REJECT         Quality GOOD/WARNING
              (Return Error)                 │
                                             ▼
                                     MLSafetyWrapper
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               ▼                             ▼                             ▼
        crop == "tomato"              crop == "potato"              crop == "other"
               │                             │                             │
               ▼                             ▼                             ▼
   PyTorchTomatoVisionProvider   PyTorchPotatoVisionProvider    VisualSymptomAnalyzerProvider
      (ml/artifacts/tomato_v1.pt)   (ml/artifacts/potato_v1.pt)    (Heuristic & Evidence Engine)
```

## Active Model Registry
| Crop Key | Model ID | Artifact Path | Classes | Accuracy (Test) | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `tomato` | `tomato-v1` | `ml/artifacts/tomato_v1.pt` | 4 | Baseline | **ACTIVE** |
| `potato` | `potato-v1` | `ml/artifacts/potato_v1.pt` | 3 | **96.83%** | **ACTIVE** |

## Predictor Class Design (`app.ml.torch_predictor.TorchPredictor`)
The `TorchPredictor` class dynamically loads model artifacts based on state metadata saved in `.pt` artifacts:
- Reads `model_version`, `classes`, `image_size`, `mean`, and `std`.
- Instantiates `HortiSentryMobileNetV3` with `num_classes = len(classes)`.
- Loads `state_dict` and switches to `eval()` mode.
- Computes top-k softmax probability distribution.
- Flags predictions with `confidence < 0.70` for expert review escalation (`needs_expert_review: True`).

## Adding New Crop Models
To add a new dedicated vision model for a future crop (e.g. `chilli-v1` or `banana-v1`):
1. Prepare manifest CSV in `data/processed/{crop}_manifest.csv`.
2. Train model via script exporting artifact to `ml/artifacts/{crop}_v1.pt`.
3. Add `PyTorch{Crop}VisionProvider` in `backend/app/ml/vision_provider.py`.
4. Register provider route in `MLSafetyWrapper` inside `backend/app/ml/predictor.py`.
5. Update `config/crops.yaml` with `vision_support_status: "trained_model"`.
