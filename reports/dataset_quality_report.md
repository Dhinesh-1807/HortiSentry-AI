# HortiSentry — Dataset Quality & Readiness Report

**Overall Dataset Status:** `READY_FOR_TRAINING`  

---

## 1. Executive Summary
This quality report documents the readiness of the HortiSentry tomato leaf dataset prior to PyTorch ML model training.

- **Total Verified Images:** 6271
- **Quality Status Distribution:** GOOD=6168, WARNING=102, REJECT=1
- **Data Leakage Safeguard:** Hash-grouped stratified 70/15/15 splitting applied.

---

## 2. Limitations & Risk Analysis
- **Controlled vs. Field Environments:** Benchmark images are captured in studio settings. Field imagery in `data/field_test/` should be evaluated separately.
- **Class Imbalance:** Monitor representation across classes to avoid minority class recall degradation during training.

---

## 3. Final Readiness Determination
**Current Status:** `READY_FOR_TRAINING`
