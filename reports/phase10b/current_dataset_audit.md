# HortiSentry — Current Multi-Crop Dataset Audit (Phase 10B)

## Executive Summary
This document provides an audit of the current **multi-crop-v1.0-benchmark** dataset (755 images) alongside the preserved baseline tomato dataset (6,271 images).

---

## 1. Baseline vs. Multi-Crop Summary
- **Tomato Baseline Dataset:** 6,271 images (`data/raw/tomato/`) | Status: `production_benchmark`
- **Multi-Crop Registered Set:** 755 images (`data/raw/multi_crop/`) | Status: `benchmark_integration`
- **Total Combined Imagery:** 7,026 images across 14 horticultural crops

---

## 2. Crop Audit Table

| Crop | Dataset Type | Total Images | Canonical Classes | Train Count | Val Count | Test Count | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tomato** | Baseline | 6271 | 4 | 4386 | 938 | 947 | Verified |
| **Potato** | Multi-Crop v1.0 | 80 | 3 | 55 | 10 | 15 | Verified |
| **Pepper** | Multi-Crop v1.0 | 55 | 2 | 38 | 7 | 10 | Verified |
| **Apple** | Multi-Crop v1.0 | 105 | 4 | 72 | 13 | 20 | Verified |
| **Grape** | Multi-Crop v1.0 | 105 | 4 | 72 | 13 | 20 | Verified |
| **Corn** | Multi-Crop v1.0 | 105 | 4 | 72 | 13 | 20 | Verified |
| **Cherry** | Multi-Crop v1.0 | 55 | 2 | 38 | 7 | 10 | Verified |
| **Peach** | Multi-Crop v1.0 | 55 | 2 | 38 | 7 | 10 | Verified |
| **Strawberry** | Multi-Crop v1.0 | 55 | 2 | 38 | 7 | 10 | Verified |
| **Orange** | Multi-Crop v1.0 | 25 | 1 | 17 | 3 | 5 | Verified |
| **Blueberry** | Multi-Crop v1.0 | 30 | 1 | 21 | 4 | 5 | Verified |
| **Raspberry** | Multi-Crop v1.0 | 30 | 1 | 21 | 4 | 5 | Verified |
| **Soybean** | Multi-Crop v1.0 | 30 | 1 | 21 | 4 | 5 | Verified |
| **Squash** | Multi-Crop v1.0 | 25 | 1 | 17 | 3 | 5 | Verified |

---

## 3. Metadata Completeness Verification
- **Source Attributed:** 100% of images link to verified source provenance.
- **Label Integrity:** Original raw labels are preserved alongside canonical class names.
- **Traceability:** Every image is registered with exact MD5 hashes and dimensions in `multi_crop_manifest.csv`.
