# HortiSentry — Phase 6 Complete Dataset Verification Report

**Project Name:** HortiSentry  
**Full Title:** HortiSentry — AI-Powered Horticultural Disease Observation and Expert Escalation System  
**Tagline:** See Early. Act Smart. Protect Crops.  

**Completion Date:** September 2, 2026  
**Final Status Determination:** `PHASE_6_COMPLETE`  

---

## 1. Dataset Source & Lineage
- **Dataset Name:** PlantVillage Tomato Leaf Disease Benchmark Dataset
- **Authors:** Hughes, A. & Salathé, M. (2015)
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Source URL:** [spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset)

---

## 2. Ingested Dataset Overview
- **Total Verified Images:** **6,271**
- **Corrupted Images:** **0**
- **Unsupported Files:** **0**
- **Directory Layout:** `data/raw/tomato/` containing exactly 4 canonical classes (`Healthy`, `Early_Blight`, `Late_Blight`, `Septoria_Leaf_Spot`).

---

## 3. Class Distribution & Imbalance Ratio

| Canonical Disease Class | Ingested Images | Distribution (%) | Pathogen / Description |
| :--- | :--- | :--- | :--- |
| **`Healthy`** | 1,591 | 25.37% | Normal foliage without lesions |
| **`Early_Blight`** | 1,000 | 15.95% | *Alternaria solani* (Minority Class) |
| **`Late_Blight`** | 1,909 | 30.44% | *Phytophthora infestans* (Majority Class) |
| **`Septoria_Leaf_Spot`** | 1,771 | 28.24% | *Septoria lycopersici* |
| **TOTAL** | **6,271** | **100.00%** | — |

- **Class Imbalance Ratio:** $\mathbf{1.91 : 1}$ (Late Blight vs. Early Blight).

---

## 4. Train / Validation / Test Split Counts (70% / 15% / 15%)

| Split Name | Image Count | Percentage | Directory Path |
| :--- | :--- | :--- | :--- |
| **Training Set** | **4,386** | 69.94% | `data/train/` |
| **Validation Set** | **938** | 14.96% | `data/validation/` |
| **Test Set** | **947** | 15.10% | `data/test/` |
| **TOTAL SPLIT COUNT** | **6,271** | **100.00%** | `data/{train,validation,test}/` |

- **Split Verification:** $4,386 + 938 + 947 = \mathbf{6,271}$.

---

## 5. Image Quality Audit Findings

- **GOOD Quality:** **6,168** images ($98.36\%$)
- **WARNING Quality:** **102** images ($1.63\%$) — Mild blur or exposure variance.
- **REJECT Quality:** **1** image ($0.02\%$)

### Inspection of the Single REJECT Image
- **Image ID:** `Late_Blight_03659`
- **Original Filename:** `9125266c-1269-43ff-b813-2052f3d16a9d___GHLB2 Leaf 8536.JPG`
- **Assigned Split:** `train`
- **Dimensions & Format:** $256\times 256$ pixels, JPEG
- **Rejection Reason:** `severe_blur` (Laplacian blur variance score = **28.52**, which is below the threshold `reject_variance = 50.0`).
- **File Safety Notice:** The file remains preserved in `data/raw/tomato/Late_Blight/` for auditability; it was not silently deleted.

---

## 6. Duplicate & Data Leakage Prevention
- **Exact Duplicate Groups:** **14** groups identified via MD5 hash comparison.
- **Near-Duplicate Pairs:** **5** candidate pairs identified via perceptual dHash.
- **Leakage Prevention Verification:** All images sharing identical MD5 or perceptual dHash signatures were grouped into the same split during stratified sampling, preventing cross-split data leakage. Zero duplicate hashes exist across `train`, `validation`, and `test` splits.

---

## 7. Manifest CSV Verification
- **Path:** `data/processed/manifest.csv`
- **Total Record Count:** **6,271** data rows (plus 1 header row = 6,272 lines).
- **Header Fields Verified:** `image_id,original_filename,class_name,split,width,height,file_format,file_size,image_hash,quality_status`.
- **Consistency Check:** 100% agreement between manifest records, audit JSON, and filesystem directories.

---

## 8. Visualization Verification
- **`reports/class_distribution.png`**: Verified generated bar chart depicting sample counts for all 4 classes across splits.
- **`reports/sample_grid.png`**: Verified generated 4-column visual grid showing representative leaf imagery for `Healthy`, `Early_Blight`, `Late_Blight`, and `Septoria_Leaf_Spot`.

---

## 9. Test Suite Verification Results

### Backend Pytest Suite
- **Command:** `.\backend\venv\Scripts\python.exe -m pytest -v`
- **Results:** **20 / 20 PASSED** ($100\%$)
- **Coverage:** Core API, health endpoints, database connection, dynamic crop loader, observation workflow, expert escalation, and dataset preparation unit tests.

### Frontend Vitest Suite
- **Command:** `cd frontend; npm test`
- **Results:** **6 / 6 PASSED** ($100\%$)
- **Coverage:** Farmer observation wizard components, AI confidence thresholds, and Expert decision panel controls.

---

## 10. Known Dataset Limitations
1. **Controlled Environment Bias:** Public benchmark leaves are photographed in studio settings with uniform backdrops ($256\times 256$). Real farm field photos may present variable lighting, shadow, wind blur, and complex soil/foliage backgrounds.
2. **Field Test Separation:** Real-world field-captured images are isolated under `data/field_test/tomato/` and are **never** mixed into training or validation splits.

---

## 11. Final Phase Readiness Determination

> [!IMPORTANT]
> **Final Status Determination:** `PHASE_6_COMPLETE`
> 
> All 11 verification dimensions have passed. The dataset structure, split ratios, manifest integrity, quality audit, zero cross-split leakage, documentation, and test suites are verified and ready for Phase 7 PyTorch ML model training.
