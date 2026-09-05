# HortiSentry — Multi-Crop Dataset Quality Audit Report (Phase 10A)

**Overall Status:** `PREPARED_FOR_MULTI_CROP`  
**Execution Date:** 2026-09-04  

---

## 1. Summary Overview
- **Total Registered Multi-Crop Images:** 755
- **Target Crops Verified:** 13 (Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry)
- **Total Canonical Disease Classes:** 28
- **Exact Duplicate Groups Identified:** 0
- **Corrupted Files Count:** 0
- **Unsupported Files Count:** 0

---

## 2. Image Quality Status Breakdown
- **GOOD Quality:** 755
- **WARNING (Mild Blur/Exposure):** 0
- **REJECT (Low Resolution/Severe Blur):** 0

---

## 3. Stratified Split Summary (70 / 15 / 15)
- **Train Set:** 520
- **Validation Set:** 95
- **Test Set:** 140

---

## 4. Preservation & Compliance Safeguards
- **Baseline Protection:** Existing 6,271 tomato images and `tomato_v1.pt` model remain 100% untouched.
- **Field Test Isolation:** `data/field_test/` remains strictly isolated for external evaluation.
- **Traceability:** Original dataset labels are preserved alongside canonical normalized classes in `multi_crop_manifest.csv`.
