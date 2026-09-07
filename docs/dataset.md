# HortiSentry — Tomato Disease Dataset Specification

**Target Crop:** Tomato (*Solanum lycopersicum*)  
**Total Images:** 6,271 images  
**Canonical Classes:** 4 classes  
**Master Fingerprint MD5:** `d501546c433bc0e204821754144bc5d9`  

---

## 1. Dataset Scope & Overview

The HortiSentry tomato dataset comprises 6,271 curated leaf images representing four canonical health/disease states:

1. **`Healthy`:** Healthy leaf tissue free of visible lesions or discoloration.
2. **`Early_Blight`:** Leaves exhibiting concentric dark spots caused by *Alternaria solani*.
3. **`Late_Blight`:** Water-soaked lesions and pale green/brown leaf damage caused by *Phytophthora infestans*.
4. **`Septoria_Leaf_Spot`:** Small circular spots with dark brown margins and gray centers caused by *Septoria lycopersici*.

---

## 2. Dataset Split Breakdown

The dataset was partitioned using stratified sampling (Seed: 42) into 70% Training, 15% Validation, and 15% Test sets:

| Disease Class | Total Images | Train (70%) | Validation (15%) | Test (15%) |
| :--- | :---: | :---: | :---: | :---: |
| **`Healthy`** | 1,591 | 1,112 | 238 | 241 |
| **`Early_Blight`** | 1,000 | 700 | 150 | 150 |
| **`Late_Blight`** | 1,909 | 1,335 | 285 | 289 |
| **`Septoria_Leaf_Spot`** | 1,771 | 1,239 | 265 | 267 |
| **Total** | **6,271** | **4,386** | **938** | **947** |

---

## 3. Dataset Audit & Quality Filtering

During Phase 6 dataset ingestion, automated image auditing (`scripts/prepare_dataset.py`) evaluated every file against `config/quality.yaml`:

- **Corrupted / Unsupported Files:** 0
- **Exact Duplicate Groups (MD5):** 14 groups identified
- **Near-Duplicate Pairs (dHash $\le 4$):** 5 pairs identified
- **Quality Status Audit:**
  - `GOOD`: 6,168 images
  - `WARNING`: 102 images
  - `REJECT`: 1 image (`Late_Blight_03659` due to severe blur, excluded from model training updates)

---

## 4. Test Set Integrity & Isolation

The 947 test images in `data/test/` were kept strictly untouched during training and hyperparameter tuning.

```
data/test/
├── Healthy/ (241 images)
├── Early_Blight/ (150 images)
├── Late_Blight/ (289 images)
└── Septoria_Leaf_Spot/ (267 images)
```

Master MD5 checksum fingerprint across all 947 test files: `d501546c433bc0e204821754144bc5d9`.
