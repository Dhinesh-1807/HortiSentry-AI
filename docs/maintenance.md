# HortiSentry — System Maintenance & Versioning Guide

## 1. Model Versioning Protocol
Model weights are tracked in the `model_versions` database table:
- **Version Convention:** `{crop_key}-v{major_version}` (e.g. `tomato-v1`).
- **Metadata Logged:** Architecture name (`MobileNetV3`), active status flag, training timestamp, and baseline accuracy.

## 2. Dynamic Configuration Maintenance (`config/crops.yaml`)
To add a new horticultural crop or update symptoms without changing code:
1. Open `config/crops.yaml`.
2. Append new crop block (e.g. `chilli` or `brinjal`).
3. Define stages, symptoms list, and target disease classes.
4. Restart FastAPI backend. The `/api/crops` endpoint automatically reflects the new crop structure.

## 3. Database Maintenance
- **Local SQLite Storage:** Located at `hortisentry.db` (or `backend/hortisentry.db`).
- **Backup Command:** Copy `hortisentry.db` to a secure backup directory prior to model updates.
